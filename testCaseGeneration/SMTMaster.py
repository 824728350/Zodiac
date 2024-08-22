### Main entry for SMT modules. This covers a wide range of implementations that
### allow SMT solver to reason about and act on: attribute/resource existence,
### attribute/resource values (e.g. Constant, CIDR), attribute dependencies
### (e.g. Equal, Unequal, CIDR Exclude, CIDR Include,) resource dependencies
### (e.g. connections, coconnections), invariant violation and conformance, 
### optimization objectives, among many others. 

import z3
import sys
sys.path.insert(0, '..')
from collections import defaultdict
import utils.utils as utils
import ipaddress
import json

class SMTMaster:
    def __init__(self):
        self.optimizer = None
        self.result = ""
        self.variableDict = defaultdict()
        self.countDict = defaultdict()
        self.violationCount_list = []
        self.violationCount_TOPO_list = []
        self.violationCount_VAL_list = []
        self.conditionCount_list = []
        self.statementCount_list = []
        self.changedCount_list = []
        self.changedCount_NAME_list =[]
        self.index = 0
        self.valueConstantDict = defaultdict()
        self.valueStringDict = defaultdict()
        self.valueCurDict = defaultdict()
        self.resourceTypeSet = set()
        self.resourceNameSet = set()
        self.oldAttrValueDict = defaultdict()
        self.violationDetailDict = defaultdict()
        
        self.vertexDict = defaultdict()
        self.vertexInputPortDict = defaultdict()
        self.vertexOutputPortDict = defaultdict()
        self.vertexNodeDict = defaultdict()
        self.VertexSort = None
        
        self.typeDict = defaultdict()
        self.typeInputPortDict = defaultdict()
        self.typeOutputPortDict = defaultdict()
        self.typeNodeDict = defaultdict()
        self.TypeSort = None
        self.portNodeDict = defaultdict()
        
        self.graphSet = None
        self.graphTypeDict = None
        self.resourceTypeDict = None
        self.graphResourceSet = None
        self.instanceDict = None
        self.given = None
        self.directly_connected = None
        self.in_solution = None
        self.tc_connected = None
        self.resource_connected = None
        self.edges = None
        self.vertex_type = None
        self.type_connected = None
        
        self.inputSum = defaultdict(list)
        self.outputSum = defaultdict(list)
        self.relatedDict = defaultdict()
        
    def optimizer_init(self, optimization, purpose):
        if optimization == True:
            self.optimizer = z3.Optimize()
        else:
            self.optimizer = z3.Solver()
        sum = z3.Int("Sum")
        sumTOPO = z3.Int("SumTOPO")
        sumVAL = z3.Int("SumVAL")
        changed = z3.Int("Changed")
        changedNAME = z3.Int("ChangedNAME")
        self.countDict["Sum"] = sum
        self.countDict["SumTOPO"] = sumTOPO
        self.countDict["SumVAL"] = sumVAL
        self.countDict["Changed"] = changed
        self.countDict["ChangedNAME"] = changedNAME
        
    def optimizer_check(self):
        return self.optimizer.check()
    def optimizer_model(self):
        return self.optimizer.model()
    def optimizer_summarize(self, optimization, purpose, ruleType, direction, iteration, resolve):
        sum = self.countDict["Sum"]
        sumTOPO = self.countDict["SumTOPO"]
        sumVAL = self.countDict["SumVAL"]
        changed = self.countDict["Changed"]
        changedNAME = self.countDict["ChangedNAME"]
        sumAllConnection = self.countDict["SumAllConnection"]

        self.optimizer.add(sumVAL == z3.Sum(self.violationCount_VAL_list))
        self.optimizer.add(sumTOPO == z3.Sum(self.violationCount_TOPO_list))
        self.optimizer.add(sum == z3.Sum(self.violationCount_list))
        self.optimizer.add(changedNAME == z3.Sum(self.changedCount_NAME_list))
        self.optimizer.add(changed == z3.Sum(self.changedCount_list))

        if purpose == "MDC":
            self.optimizer.add(changed == 0)
            self.optimizer.add(changedNAME == 0)
            self.optimizer.add(sumAllConnection == 0)
        elif purpose == "GEN" or purpose == "AGGTOPO" or purpose == "AGGATTR":
            ### recall that ATTR rules are treated differently during the first round! minimizing changes were prioritized to maintain mutation quality             
            if ruleType != "ATTR" or iteration != 0:
                print("Minimizing amount of violations")
                self.optimizer.add(sumVAL == 0)
                if resolve == True:
                    self.optimizer.minimize(sum)
                else:
                    self.optimizer.add(sum == 0)
                self.optimizer.minimize(sumAllConnection)
                self.optimizer.minimize(changedNAME)
                self.optimizer.minimize(changed)
            else:
                print("Minimizing amount of changes")
                self.optimizer.minimize(changedNAME)
                self.optimizer.minimize(changed)
                self.optimizer.minimize(sumVAL)
                self.optimizer.minimize(sum)
                self.optimizer.minimize(sumAllConnection)
            
        return self.countDict
    
    def generation_placeholder(self, manifest):
        if manifest == "Condition":
            conditionCount_index = z3.Int(f"conditionCount_{self.index}")
            self.conditionCount_list.append(conditionCount_index)
            self.countDict[f"conditionCount_{self.index}"] = conditionCount_index
            self.optimizer.add(conditionCount_index == 0)
        elif manifest == "Statement":
            statementCount_index = z3.Int(f"statementCount_{self.index}")
            self.statementCount_list.append(statementCount_index)
            self.countDict[f"statementCount_{self.index}"] = statementCount_index
            self.optimizer.add(statementCount_index == 1)
            
    def generate_equality_mutation(self, valueArray, startIndex, optimization, vNodeCount):
        ### add equality mutation smt constraints, makes sure the old attributes are contained in the semantice type system.
        self.index = startIndex
        for nodeName1, nodeValue1, nodeName2, nodeValue2, relation, manifest in valueArray:
            value_old1 = z3.StringVal(nodeValue1)
            if nodeName1 not in self.variableDict:
                value_new1_name = f"{nodeName1}_value"
                value_new1 = z3.String(value_new1_name)
                self.variableDict[nodeName1] = [value_new1] 
                changedCount_index1 = z3.Int(f"changedCount_{nodeName1}")
                if "name" == nodeName1.split(".")[-1]:
                    self.changedCount_NAME_list.append(changedCount_index1)
                else:
                    self.changedCount_list.append(changedCount_index1)
                self.countDict[f"changedCount_{nodeName1}"] = changedCount_index1
                self.optimizer.add(changedCount_index1 == z3.If(value_new1 == value_old1, 0, 1)) 
                if optimization == False:
                    self.optimizer.add_soft(value_new1 == value_old1, weight = 100)
                self.oldAttrValueDict[nodeName1] = nodeValue1
            else:
                if len(self.variableDict[nodeName1]) == 1:
                    value_new1 = self.variableDict[nodeName1][0]
                else:
                    self.generation_placeholder(manifest)
                    continue
            
            value_old2 = z3.StringVal(nodeValue2)
            if relation in ["Equal", "Unequal"]:
                nodeName2 = nodeName2+"_111"
            if nodeName2 not in self.variableDict:
                value_new2_name = f"{nodeName2}_value"
                value_new2 = z3.String(value_new2_name)
                self.variableDict[nodeName2] = [value_new2] 
                changedCount_index2 = z3.Int(f"changedCount_{nodeName2}")
                if "name" == nodeName2.split(".")[-1]:
                    self.changedCount_NAME_list.append(changedCount_index2)
                else:
                    self.changedCount_list.append(changedCount_index2)
                self.countDict[f"changedCount_{nodeName2}"] = changedCount_index2
                self.optimizer.add(changedCount_index2 == z3.If(value_new2 == value_old2, 0, 1))
                if optimization == False:
                    self.optimizer.add_soft(value_new1 == value_old1, weight = 100)
                self.oldAttrValueDict[nodeName2] = nodeValue2  
            else:
                if len(self.variableDict[nodeName2]) == 1:
                    value_new2 = self.variableDict[nodeName2][0]
                else:
                    self.generation_placeholder(manifest)
                    continue
                
            if relation in ["Equal", "Unequal"]:    
                nodeName2 = nodeName2[:-4]
            nodeResourceType1 = nodeName1.split(".")[0]
            nodeResourceAttr1 = ".".join(nodeName1.split(".")[2:])
            nodeResourceType2 = nodeName2.split(".")[0]
            nodeResourceAttr2 = ".".join(nodeName2.split(".")[2:])
            
            ### special treatment for aribtrary string values
            valueList1, valueList2 = [], []
            maxAmount = 10
            if vNodeCount > maxAmount:
                maxAmount = vNodeCount
            if nodeResourceAttr1 in ["name", "location"]:
                tempList = []
                for nodeResourceType in self.valueStringDict:
                    if nodeResourceAttr1 in self.valueStringDict[nodeResourceType]:
                        for item in self.valueStringDict[nodeResourceType][nodeResourceAttr1]:
                            forbiddenString = r'\/"[]:|<>+=;,?*@&~!#$%^()_{}'
                            if "hold" not in item and not any(ele in item for ele in forbiddenString):
                                tempList.append(item)
                valueList1 = sorted(tempList)[(-1*maxAmount):]
            else:
                tempList = []
                for item in self.valueStringDict[nodeResourceType1][nodeResourceAttr1]:
                    if "hold" not in item:
                        tempList.append(item)
                valueList1 = sorted(tempList)[(-1*maxAmount):]
            if nodeResourceAttr2 in ["name", "location"]:
                tempList = []
                for nodeResourceType in self.valueStringDict:
                    if nodeResourceAttr2 in self.valueStringDict[nodeResourceType]:
                        for item in self.valueStringDict[nodeResourceType][nodeResourceAttr2]:
                            forbiddenString = r'\/"[]:|<>+=;,?*@&~!#$%^()_{}'
                            if "hold" not in item and not any(ele in item for ele in forbiddenString):
                                tempList.append(item)
                valueList2 = sorted(tempList)[(-1*maxAmount):]
            else:
                tempList = []
                for item in self.valueStringDict[nodeResourceType2][nodeResourceAttr2]:
                    if "hold" not in item:
                        tempList.append(item)
                valueList2 = sorted(tempList)[(-1*maxAmount):]
                #valueList2 = sorted(self.valueStringDict[nodeResourceType2][nodeResourceAttr2])[-10:]
            
            if vNodeCount != 0 and (len(valueList1) <= vNodeCount or len(valueList2) <= vNodeCount):
                valueListAmend = []
                valueList1, valueList2 = [], []
                if "name" in nodeResourceAttr1 or "name" in nodeResourceAttr2:
                    valueListAmend = [f"zodiacyiming{i}" for i in range(max(vNodeCount + 2 - min(len(valueList1), len(valueList2)), 0))]
                if "priority" in nodeResourceAttr1 or "priority" in nodeResourceAttr2 or "lun" in nodeResourceAttr1 or "lun" in nodeResourceAttr2:
                    valueListAmend = [str(20+i) for i in range(max(vNodeCount + 2 - min(len(valueList1), len(valueList2)), 0))]
                valueList1 += valueListAmend
                valueList2 += valueListAmend
            for nodeValue in [nodeValue1, nodeValue2]:
                if nodeValue not in valueList1:
                    valueList1.append(nodeValue)
                if nodeValue not in valueList2:
                    valueList2.append(nodeValue)
            valueList1 = list(set(valueList1))
            valueList2 = list(set(valueList2))
            
            self.optimizer.add_soft(z3.Or([value_new1 == value for value in valueList1]))
            self.optimizer.add_soft(z3.Or([value_new2 == value for value in valueList2]))
            
            if manifest == "Condition":
                conditionCount_index = z3.Int(f"conditionCount_{self.index}")
                self.conditionCount_list.append(conditionCount_index)
                self.countDict[f"conditionCount_{self.index}"] = conditionCount_index
                if "Equal" in relation:
                    self.optimizer.add(conditionCount_index == z3.If(value_new1 == value_new2, 1, 0))
                elif "Unequal" in relation:
                    self.optimizer.add(conditionCount_index == z3.If(value_new1 != value_new2, 1, 0))
            elif manifest == "Statement":
                statementCount_index = z3.Int(f"statementCount_{self.index}")
                self.statementCount_list.append(statementCount_index)
                self.countDict[f"statementCount_{self.index}"] = statementCount_index
                if "Equal" in relation:
                    self.optimizer.add(statementCount_index == z3.If(value_new1 == value_new2, 1, 0))
                elif "Unequal" in relation:
                    self.optimizer.add(statementCount_index == z3.If(value_new1 != value_new2, 1, 0))
                
            else:
                print("Something went wrong, unable to parse SMT manifest Equality!")
                return
            self.index += 1
            
    def generate_CIDR_mutation(self, valueArray, startIndex, optimization):
        ### add CIDR mutation smt constraints, makes sure the old attributes are contained in the semantice type system.
        self.index = startIndex
        for prefixName1, prefixCIDR1, prefixName2, prefixCIDR2, relation, manifest in valueArray:
            ### processing the first ip cidr range: two possiblities, mutate or not!
            try:
                parsedCIDR1 = ipaddress.ip_network(prefixCIDR1)
                parsedCIDR2 = ipaddress.ip_network(prefixCIDR2)
            except:
                self.generation_placeholder(manifest)
                continue
            ip_old1, len_old1 = prefixCIDR1.split("/")
            bv_old1 = utils.ip_to_bv(ip_old1)
            len_old1 = int(len_old1)
            if prefixName1 not in self.variableDict:
                bv_new1_name = f"{prefixName1}_bv"
                bv_new1 = z3.BitVec(bv_new1_name, 32)
                len_new1_name = f"{prefixName1}_len"
                len_new1 = z3.Int(len_new1_name)
                self.variableDict[prefixName1] = [bv_new1, len_new1]
                changedCount_index1 = z3.Int(f"changedCount_{prefixName1}")
                if "name" == prefixName1.split(".")[-1]:
                    self.changedCount_NAME_list.append(changedCount_index1)
                else:
                    self.changedCount_list.append(changedCount_index1)
                self.countDict[f"changedCount_{prefixName1}"] = changedCount_index1
                self.optimizer.add(len_new1 == len_old1)
                self.optimizer.add(changedCount_index1 == z3.If(z3.And(bv_new1 == bv_old1, len_new1 == len_old1), 0, 1))
                if optimization == False:
                    self.optimizer.add_soft(bv_new1 == bv_old1, weight = 50)
                    self.optimizer.add_soft(len_new1 == len_old1, weight = 50)
                self.oldAttrValueDict[prefixName1] = prefixCIDR1 
                
            else:
                try:
                    bv_new1 = self.variableDict[prefixName1][0]
                    len_new1 = self.variableDict[prefixName1][1]
                except:
                    self.generation_placeholder(manifest)
                    continue
                
            ### processing the second ip cidr range: two possiblities, mutate or not!
            ip_old2, len_old2 = prefixCIDR2.split("/")
            bv_old2 = utils.ip_to_bv(ip_old2)
            len_old2 = int(len_old2)
            if relation in ["CIDRInclude", "CIDRExclude"]:
                prefixName2 = prefixName2+"_111"
            if prefixName2 not in self.variableDict:
                bv_new2_name = f"{prefixName2}_bv"
                bv_new2 = z3.BitVec(bv_new2_name, 32)
                len_new2_name = f"{prefixName2}_len"
                len_new2 = z3.Int(len_new2_name)
                self.variableDict[prefixName2] = [bv_new2, len_new2]
                changedCount_index2 = z3.Int(f"changedCount_{prefixName2}")
                if "name" == prefixName2.split(".")[-1]:
                    self.changedCount_NAME_list.append(changedCount_index2)
                else:
                    self.changedCount_list.append(changedCount_index2)
                self.countDict[f"changedCount_{prefixName2}"] = changedCount_index2
                self.optimizer.add(changedCount_index2 == z3.If(z3.And(bv_new2 == bv_old2, len_new2 == len_old2), 0, 1)) 
                self.optimizer.add(len_new2 == len_old2)
                if optimization == False:
                    self.optimizer.add_soft(bv_new2 == bv_old2, weight = 50)
                    self.optimizer.add_soft(len_new2 == len_old2, weight = 50)
                self.oldAttrValueDict[prefixName2] = prefixCIDR2 
            else:
                try:
                    bv_new2 = self.variableDict[prefixName2][0]
                    len_new2 = self.variableDict[prefixName2][1]
                except:
                    self.generation_placeholder(manifest)
                    continue
            if relation in ["CIDRInclude", "CIDRExclude"]:
                prefixName2 = prefixName2[:-4]
            ### We must make sure the generated CIDR ranges are valid by themselves!
            mask1 = utils.ip_to_bv(str(utils.len_to_mask(len_old1)))
            self.optimizer.add((bv_new1 & mask1) == bv_new1)
            mask2 = utils.ip_to_bv(str(utils.len_to_mask(len_old2)))
            self.optimizer.add((bv_new2 & mask2) == bv_new2)
            
            if manifest == "Condition":
                minLen = min(len_old1, len_old2)
                conditionCount_index = z3.Int(f"conditionCount_{self.index}")
                self.conditionCount_list.append(conditionCount_index)
                self.countDict[f"conditionCount_{self.index}"] = conditionCount_index
                if "CIDRExclude" in relation:
                    self.optimizer.add(conditionCount_index == z3.If(z3.Extract(31, 32 - minLen, bv_new1) != z3.Extract(31, 32 - minLen, bv_new2), 1, 0))
                elif "CIDRInclude" in relation:
                    self.optimizer.add(conditionCount_index == z3.If(z3.And(z3.Extract(31, 32 - minLen, bv_new1) == z3.Extract(31, 32 - minLen, bv_new2), len_new2 <= len_new1), 1, 0))
            elif manifest == "Statement":
                minLen = min(len_old1, len_old2)
                statementCount_index = z3.Int(f"statementCount_{self.index}")
                self.statementCount_list.append(statementCount_index)
                self.countDict[f"statementCount_{self.index}"] = statementCount_index
                if "CIDRExclude" in relation:
                    self.optimizer.add(statementCount_index == z3.If(z3.Extract(31, 32 - minLen, bv_new1) != z3.Extract(31, 32 - minLen, bv_new2), 1, 0))
                elif "CIDRInclude" in relation:
                    self.optimizer.add(statementCount_index == z3.If(z3.And(z3.Extract(31, 32 - minLen, bv_new1) == z3.Extract(31, 32 - minLen, bv_new2), len_new2 <= len_new1), 1, 0))
            else:
                print("Something went wrong, unable to parse SMT manifest CIDR!")
                return
            
            self.optimizer.minimize(z3.Abs(bv_new1-bv_old1) + z3.Abs(bv_new2-bv_old2))
            self.optimizer.add(bv_new1 >= bv_old1)
            self.optimizer.add(bv_new2 >= bv_old2)
            self.index += 1
    
    def generate_mask_mutation(self, valueArray, startIndex, optimization):
        self.index = startIndex
        for prefixName1, prefixCIDR1, truthValue1, operation, manifest in valueArray:
            ip_old1, len_old1 = prefixCIDR1.split("/")
            bv_old1 = utils.ip_to_bv(ip_old1)
            len_old1 = int(len_old1)
            len_truth1 = int(truthValue1)
            if prefixName1 not in self.variableDict:
                bv_new1_name = f"{prefixName1}_bv"
                bv_new1 = z3.BitVec(bv_new1_name, 32)
                len_new1_name = f"{prefixName1}_len"
                len_new1 = z3.Int(len_new1_name)
                self.variableDict[prefixName1] = [bv_new1, len_new1]
                changedCount_index1 = z3.Int(f"changedCount_{prefixName1}")
                if "name" == prefixName1.split(".")[-1]:
                    self.changedCount_NAME_list.append(changedCount_index1)
                else:
                    self.changedCount_list.append(changedCount_index1)
                self.countDict[f"changedCount_{prefixName1}"] = changedCount_index1
                self.optimizer.add_soft(len_new1 == len_old1)
                self.optimizer.add(changedCount_index1 == z3.If(z3.And(bv_new1 == bv_old1, len_new1 == len_old1), 0, 1))
                if optimization == False:
                    self.optimizer.add_soft(bv_new1 == bv_old1, weight = 50)
                    self.optimizer.add_soft(len_new1 == len_old1, weight = 50)
                self.oldAttrValueDict[prefixName1] = prefixCIDR1 
                
            else:
                bv_new1 = self.variableDict[prefixName1][0]
                len_new1 = self.variableDict[prefixName1][1]
            ### We must make sure the generated CIDR ranges are valid by themselves!
            mask1 = utils.ip_to_bv(str(utils.len_to_mask(len_old1)))
            self.optimizer.add((bv_new1 & mask1) == bv_new1)
            
            if manifest == "Condition":
                conditionCount_index = z3.Int(f"conditionCount_{self.index}")
                self.conditionCount_list.append(conditionCount_index)
                self.countDict[f"conditionCount_{self.index}"] = conditionCount_index
                self.optimizer.add(conditionCount_index == z3.If(len_new1 <= len_truth1, 1, 0))
            elif manifest == "Statement":
                statementCount_index = z3.Int(f"statementCount_{self.index}")
                self.statementCount_list.append(statementCount_index)
                self.countDict[f"statementCount_{self.index}"] = statementCount_index
                self.optimizer.add(statementCount_index == z3.If(len_new1 <= len_truth1, 1, 0))
            else:
                print("Something went wrong, unable to parse SMT manifest MASK!")
                return
            
            self.optimizer.minimize(z3.Abs(bv_new1-bv_old1))
            self.optimizer.add(bv_new1 >= bv_old1)
            self.index += 1
            
    def generate_enum_mutation(self, valueArray, startIndex, optimization):
        ### add existence/absence/constant mutation smt constraints, makes sure the old attributes are contained in the semantice type system.
        self.index = startIndex
        for nodeName1, nodeValue1, truthValue1, operation, manifest in valueArray:
            value_old1 = z3.StringVal(nodeValue1)
            if nodeName1 not in self.variableDict:
                value_new1_name = f"{nodeName1}_value"
                value_new1 = z3.String(value_new1_name)
                self.variableDict[nodeName1] = [value_new1]  
                changedCount_index = z3.Int(f"changedCount_{nodeName1}")
                if "name" == nodeName1.split(".")[-1] or "type" in nodeName1.split(".")[-1] or "size" in nodeName1.split(".")[-1] or "sku" in nodeName1.split(".")[-1]:
                    self.changedCount_NAME_list.append(changedCount_index)
                else:
                    self.changedCount_list.append(changedCount_index)
                self.countDict[f"changedCount_{nodeName1}"] = changedCount_index
                self.optimizer.add(changedCount_index == z3.If(value_new1 == value_old1, 0, 1))
                if optimization == False:
                    self.optimizer.add_soft(value_new1 == value_old1, weight = 100)
                self.oldAttrValueDict[nodeName1] = nodeValue1 
            else:
                value_new1 = self.variableDict[nodeName1][0]
            
            valueList1 = []
            if operation in ["Absence", "Existence", "AbsenceComboUp", "AbsenceComboDown", "ExistenceComboUp", "ExistenceComboDown"]:
                valueList1 = ["Absence", "Existence"]
            elif operation in ["Constant", "ConstantComboUp", "ConstantComboDown", "NonConstant", "NonConstantComboDown", "NonConstantComboUp"]:
                nodeType1 = nodeName1.split(".")[0]
                nodeAttr1 = ".".join(nodeName1.split(".")[2:])
                if nodeAttr1 in ["name", "location", "sku", "tier", "size"] or "sku" in nodeAttr1:
                    valueList1 = self.valueConstantDict[nodeType1][nodeAttr1][:10]
                else:
                    valueList1 = self.valueStringDict[nodeType1][nodeAttr1][:10]
                if nodeValue1 not in valueList1:
                    valueList1.append(nodeValue1)
                if truthValue1 not in valueList1:
                    valueList1.append(truthValue1)
            self.optimizer.add(z3.Or([value_new1 == value for value in valueList1]))
            
            if manifest == "Condition":
                conditionCount_index = z3.Int(f"conditionCount_{self.index}")
                self.conditionCount_list.append(conditionCount_index)
                self.countDict[f"conditionCount_{self.index}"] = conditionCount_index
                if operation not in ["NonConstant", "NonConstantComboDown", "NonConstantComboUp"]:
                    self.optimizer.add(conditionCount_index == z3.If(value_new1 == truthValue1, 1, 0))
                else:
                    self.optimizer.add(conditionCount_index == z3.If(value_new1 != truthValue1, 1, 0))
            elif manifest == "Statement":
                statementCount_index = z3.Int(f"statementCount_{self.index}")
                self.statementCount_list.append(statementCount_index)
                self.countDict[f"statementCount_{self.index}"] = statementCount_index
                if operation not in ["NonConstant", "NonConstantComboDown", "NonConstantComboUp"]:
                    self.optimizer.add(statementCount_index == z3.If(value_new1 == truthValue1, 1, 0))
                else:
                    self.optimizer.add(statementCount_index == z3.If(value_new1 != truthValue1, 1, 0))
            else:
                print("Something went wrong, unable to parse SMT manifest Enum!")
                return
            self.index += 1
    
    def generate_bin_enum_mutation(self, valueArray, startIndex, optimization):
        ### add existence/absence/constant mutation smt constraints, makes sure the old attributes are contained in the semantice type system.
        self.index = startIndex
        for nodeName1, nodeValue1, truthValue1, nodeName2, nodeValue2, truthValue2, operation, manifest in valueArray:
            value_old1 = z3.StringVal(nodeValue1)
            if nodeName1 not in self.variableDict:
                value_new1_name = f"{nodeName1}_value"
                value_new1 = z3.String(value_new1_name)
                self.variableDict[nodeName1] = [value_new1]  
                changedCount_index = z3.Int(f"changedCount_{nodeName1}")
                self.changedCount_list.append(changedCount_index)
                self.countDict[f"changedCount_{nodeName1}"] = changedCount_index
                self.optimizer.add(changedCount_index == z3.If(value_new1 == value_old1, 0, 1))
                if optimization == False:
                    self.optimizer.add_soft(value_new1 == value_old1, weight = 100)
                self.oldAttrValueDict[nodeName1] = nodeValue1 
            else:
                value_new1 = self.variableDict[nodeName1][0]
                
            value_old2 = z3.StringVal(nodeValue2)
            if nodeName2 not in self.variableDict:
                value_new2_name = f"{nodeName2}_value"
                value_new2 = z3.String(value_new2_name)
                self.variableDict[nodeName2] = [value_new2]  
                changedCount_index = z3.Int(f"changedCount_{nodeName2}")
                self.changedCount_list.append(changedCount_index)
                self.countDict[f"changedCount_{nodeName2}"] = changedCount_index
                self.optimizer.add(changedCount_index == z3.If(value_new2 == value_old2, 0, 1))
                if optimization == False:
                    self.optimizer.add_soft(value_new2 == value_old2, weight = 100)
                self.oldAttrValueDict[nodeName2] = nodeValue2 
            else:
                value_new2 = self.variableDict[nodeName2][0]
            
            valueList1, valueList2 = [], []
            if operation in ["BinConstantCombo", "BinConstant"]:
                nodeType1 = nodeName1.split(".")[0]
                nodeAttr1 = ".".join(nodeName1.split(".")[2:])
                if nodeAttr1 in ["name", "location", "sku", "tier", "size"] or "sku" in nodeAttr1:
                    valueList1 = self.valueConstantDict[nodeType1][nodeAttr1][:10]
                else:
                    valueList1 = self.valueStringDict[nodeType1][nodeAttr1][:10]
                nodeType2 = nodeName2.split(".")[0]
                nodeAttr2 = ".".join(nodeName2.split(".")[2:])
                if nodeAttr2 in ["name", "location", "sku", "tier", "size"] or "sku" in nodeAttr2:
                    valueList2 = self.valueConstantDict[nodeType2][nodeAttr2][:10]
                else:
                    valueList2 = self.valueStringDict[nodeType2][nodeAttr2][:10]
                for nodeValue in [nodeValue1, nodeValue2]:
                    if nodeValue not in valueList1:
                        valueList1.append(nodeValue)
                    if nodeValue not in valueList2:
                        valueList2.append(nodeValue)
                for truthValue in [truthValue1, truthValue2]:
                    if truthValue not in valueList1:
                        valueList1.append(truthValue)
                    if truthValue not in valueList2:
                        valueList2.append(truthValue)
            self.optimizer.add(z3.Or([value_new1 == value for value in valueList1]))
            self.optimizer.add(z3.Or([value_new2 == value for value in valueList2]))
            
            if manifest == "Condition":
                conditionCount_index = z3.Int(f"conditionCount_{self.index}")
                self.conditionCount_list.append(conditionCount_index)
                self.countDict[f"conditionCount_{self.index}"] = conditionCount_index
                self.optimizer.add(conditionCount_index == z3.If(z3.And(value_new1 == truthValue1, value_new2 == truthValue2), 1, 0))
            elif manifest == "Statement":
                statementCount_index = z3.Int(f"statementCount_{self.index}")
                self.statementCount_list.append(statementCount_index)
                self.countDict[f"statementCount_{self.index}"] = statementCount_index
                self.optimizer.add(statementCount_index == z3.If(z3.Or(value_new1 != truthValue1, value_new2 == truthValue2), 1, 0))
            else:
                print("Something went wrong, unable to parse SMT manifest Enum!")
                return
            self.index += 1
            
    ### Note that there is mismatch on what dependencyList means between this function and preprocessing functions!!!
    def generate_reference_infra(self, refArray, originalRefArray, plan, rawPlan, dependencyList, virtualResourceDict, waivedSet, purpose, additionalGraphTypeDict):
        ### add resource references, both existing and virtual, to define search space for topo mutations.
        self.VertexSort = z3.Datatype("VertexSort")
        self.TypeSort = z3.Datatype("TypeSort")
        self.graphSet = set() 
        self.graphTypeDict = defaultdict(int)
        self.resourceTypeDict = defaultdict(int)
        self.instanceDict = defaultdict()
        self.dependencyPortSet = set()
        self.dependencyNodeDict = defaultdict(list)
        virtualResourceList = []
        globalAncestorDict = json.load(open("../regoFiles/globalAncestorDict.json", "r"))
        
        for key in list(virtualResourceDict.keys()):
            virtualResourceList += virtualResourceDict[key]
        print("virtualResourceList", virtualResourceList)
        ### construct all resource node and port type representation
        for _, resourceBlock in enumerate(plan):
            resourceType = resourceBlock["type"]
            resourceName = resourceBlock["address"]
            self.resourceTypeSet.add(resourceType)
            self.resourceNameSet.add(resourceName)
       
        for resourceType in dependencyList:
            if resourceType not in self.typeDict and resourceType in self.resourceTypeSet:
                value_resourceType = f"{resourceType}"
                self.TypeSort.declare(value_resourceType)
                self.typeDict[resourceType] = "Node"
            for inputNodeType, outputNodeType, inputPortType, outputPortType in dependencyList[resourceType]:
                if purpose in ["AGGTOPO", "AGGATTR"] and inputNodeType == outputNodeType:
                    continue
                outputPortType = outputNodeType + "." + outputPortType
                if outputPortType not in self.typeDict and outputNodeType in self.resourceTypeSet:
                    value_outputPortType = f"{outputPortType}"
                    self.TypeSort.declare(value_outputPortType)
                    self.typeDict[outputPortType] = "OutputPort"
                inputPortType = inputNodeType + "." + inputPortType
                if inputPortType not in self.typeDict and inputNodeType in self.resourceTypeSet:
                    value_inputPortType = f"{inputPortType}"
                    self.TypeSort.declare(value_inputPortType)
                    self.typeDict[inputPortType] = "InputPort"
        
        ### create resource node and port type SMT variables    
        self.TypeSort = self.TypeSort.create()
        for vertex in list(self.typeDict.keys()):
            if self.typeDict[vertex] == "Node":
                self.typeNodeDict[vertex] = getattr(self.TypeSort, str(vertex))
            elif self.typeDict[vertex] == "InputPort":
                self.typeInputPortDict[vertex] = getattr(self.TypeSort, str(vertex))
            elif self.typeDict[vertex] == "OutputPort":
                self.typeOutputPortDict[vertex] = getattr(self.TypeSort, str(vertex))
            self.typeDict[vertex] = getattr(self.TypeSort, str(vertex))
        
        ### construct all resource node and port entity representation
        resourceInputPortList = defaultdict(list)
        for _, resourceBlock in enumerate(plan):
            resourceType = resourceBlock["type"]
            resourceName = resourceBlock["address"]
            if resourceType not in dependencyList:
                continue
            if resourceName not in self.vertexDict:
                self.VertexSort.declare(resourceName)
                self.vertexDict[resourceName] = "Node"
                self.instanceDict[resourceName] = resourceType
                resourceInputPortList[resourceName] = []
            for key in dependencyList:
                for type1, type2, ref1, ref2 in dependencyList[key]:
                    if purpose in ["AGGTOPO", "AGGATTR"] and type1 == type2:
                        continue
                    if type1 == resourceType:
                        resourceInputPort = resourceName + "." + ref1
                        if resourceInputPort not in self.vertexDict:
                            self.VertexSort.declare(resourceInputPort)
                            self.vertexDict[resourceInputPort] = "InputPort"
                            self.instanceDict[resourceInputPort] = resourceType + "." + ref1
                            resourceInputPortList[resourceName].append(resourceInputPort)
                    elif type2 == resourceType:
                        resourceOutputPort = resourceName + "." + ref2
                        if resourceOutputPort not in self.vertexDict:
                            self.VertexSort.declare(resourceOutputPort)
                            self.vertexDict[resourceOutputPort] = "OutputPort"
                            self.instanceDict[resourceOutputPort] = resourceType + "." + ref2
        
        ### create resource node and port entity SMT variables 
        self.VertexSort.declare("rootNode")
        self.VertexSort = self.VertexSort.create()
        for vertex in list(self.vertexDict.keys()):
            if self.vertexDict[vertex] == "Node":
                self.vertexNodeDict[vertex] = getattr(self.VertexSort, str(vertex))
            elif self.vertexDict[vertex] == "InputPort":
                self.vertexInputPortDict[vertex] = getattr(self.VertexSort, str(vertex))
            elif self.vertexDict[vertex] == "OutputPort":
                self.vertexOutputPortDict[vertex] = getattr(self.VertexSort, str(vertex))
            self.vertexDict[vertex] = getattr(self.VertexSort, str(vertex))        
        self.vertexDict["rootNode"] = getattr(self.VertexSort, str("rootNode"))
        
        for inputNodeName, outputNodeName, inputPortName, outputPortName, _, _ in refArray:
            outputNodeType = outputNodeName.split(".")[0]
            inputNodeType = inputNodeName.split(".")[0]
            if outputNodeType not in dependencyList or inputNodeType not in dependencyList:
                continue
            if outputNodeType not in self.resourceTypeSet or inputNodeType not in self.resourceTypeSet:
                continue
            
            outputPortType = outputNodeName.split(".")[0] + "." + outputPortName
            outputPortName = outputNodeName + "." + outputPortName
            inputPortType = inputNodeName.split(".")[0] + "." + inputPortName
            inputPortName = inputNodeName + "." + inputPortName
            
            if outputNodeName in self.resourceNameSet and inputNodeName in self.resourceNameSet:
                self.graphSet.add((outputPortName, inputPortName))
                self.dependencyPortSet.add((inputNodeName, outputNodeName, inputPortName, outputPortName))
                
        for inputNodeName, outputNodeName, inputPortName, outputPortName, _, _ in originalRefArray:
            outputNodeType = outputNodeName.split(".")[0]
            inputNodeType = inputNodeName.split(".")[0]
            if outputNodeType not in dependencyList or inputNodeType not in dependencyList:
                continue
            if outputNodeType not in self.resourceTypeSet or inputNodeType not in self.resourceTypeSet:
                continue
            
            outputPortType = outputNodeName.split(".")[0] + "." + outputPortName
            outputPortName = outputNodeName + "." + outputPortName
            inputPortType = inputNodeName.split(".")[0] + "." + inputPortName
            inputPortName = inputNodeName + "." + inputPortName
            
            self.graphTypeDict[(outputPortType, inputPortType, inputNodeType)] += 1
        
        ### Gather legal connectivity information from existing resources
        for _, resourceBlock in enumerate(rawPlan):
            resourceType = resourceBlock["type"]
            resourceName = resourceBlock["address"]
            if resourceType not in dependencyList:
                continue
            self.resourceTypeDict[resourceType] += 1
        
        ### declare Z3 Functions to express connectivity in SMT       
        self.given = z3.Function(
            f"given", self.VertexSort, self.VertexSort, z3.BoolSort()
        )
        self.directly_connected = z3.Function(
            f"directly_connected", self.VertexSort, self.VertexSort, z3.BoolSort()
        )
        self.resource_connected = z3.Function(
            f"resource_connected", self.VertexSort, self.VertexSort, z3.BoolSort()
        )
        self.ancestor_connected = z3.Function(
            f"ancestor_connected", self.VertexSort, self.VertexSort, z3.BoolSort()
        )
        self.in_solution = z3.Function(
            f"in_solution", self.VertexSort, self.VertexSort, z3.BoolSort()
        )
        self.vertex_type = z3.Function(
            f"vertex_type", self.VertexSort, self.TypeSort, z3.BoolSort()
        )
        self.type_connection = z3.Function(
            f"type_connection", self.TypeSort, self.TypeSort, z3.BoolSort()
        )
        
        ### create existing edges among existing input-output port pairs, virtual nodes ignored
        for edge in self.graphSet:
            self.optimizer.add(self.given(self.vertexDict[edge[0]], self.vertexDict[edge[1]]))
            self.optimizer.add(z3.Not(self.in_solution(self.vertexDict[edge[0]], self.vertexDict[edge[1]])))
        
        ### create existing edges among resource nodes and their ports, virutal nodes included
        for _, resourceBlock in enumerate(plan):
            resourceType = resourceBlock["type"]
            resourceName = resourceBlock["address"]
            if resourceType not in dependencyList:
                continue
            for key in dependencyList:
                for type1, type2, ref1, ref2 in dependencyList[key]:
                    if purpose in ["AGGTOPO", "AGGATTR"] and type1 == type2:
                        continue
                    if type1 == resourceType:
                        resourceInputPort = resourceName + "." + ref1
                        self.optimizer.add(self.given(self.vertexDict[resourceInputPort], self.vertexDict[resourceName]))
                        self.optimizer.add(z3.Not(self.in_solution(self.vertexDict[resourceInputPort], self.vertexDict[resourceName])))
                        self.optimizer.add(
                            self.directly_connected(self.vertexDict[resourceInputPort], self.vertexDict[resourceName])
                            == z3.Or(
                                self.in_solution(self.vertexDict[resourceInputPort], self.vertexDict[resourceName]),
                                self.given(self.vertexDict[resourceInputPort], self.vertexDict[resourceName]),
                            ),
                        )
                    elif type2 == resourceType:
                        resourceOutputPort = resourceName + "." + ref2
                        self.optimizer.add(self.given(self.vertexDict[resourceName], self.vertexDict[resourceOutputPort]))
                        self.optimizer.add(z3.Not(self.in_solution(self.vertexDict[resourceName], self.vertexDict[resourceOutputPort])))
                        self.optimizer.add(
                            self.directly_connected(self.vertexDict[resourceName], self.vertexDict[resourceOutputPort])
                            == z3.Or(
                                self.in_solution(self.vertexDict[resourceName], self.vertexDict[resourceOutputPort]),
                                self.given(self.vertexDict[resourceName], self.vertexDict[resourceOutputPort]),
                            ),
                        )
                    
        ### connect rootnode with top entities. Pay attention!
        for resourceName in resourceInputPortList:
            if len(resourceInputPortList[resourceName]) == 0:
                print("top resource name: ", resourceName)
                if resourceName not in virtualResourceList:
                    self.optimizer.add(self.directly_connected(self.vertexDict["rootNode"], self.vertexDict[resourceName]))
            else:
                self.optimizer.add(z3.Not(self.directly_connected(self.vertexDict["rootNode"], self.vertexDict[resourceName])))
        for inputPort in self.vertexInputPortDict:
            self.optimizer.add(z3.Not(self.directly_connected(self.vertexDict["rootNode"], self.vertexDict[inputPort])))
        for outputPort in self.vertexOutputPortDict:
            self.optimizer.add(z3.Not(self.directly_connected(self.vertexDict["rootNode"], self.vertexDict[outputPort])))
       
        ### declare legal connection (edge and node connection) types
        for edge in additionalGraphTypeDict:
            self.graphTypeDict[edge] = additionalGraphTypeDict[edge]
        additionalTuple = set()
        
        if purpose != "AGGATTR":
            ### if purpose == AGGATTR, then skip complex topology legal connection reasoning
            for edge in self.graphTypeDict:
                self.optimizer.add(self.type_connection(self.typeDict[edge[0]], self.typeDict[edge[1]]))
                print(edge, self.graphTypeDict[edge], self.resourceTypeDict[edge[2]])
                ### determining whether dependency is mandatory(required) or optional
                if self.graphTypeDict[edge] < self.resourceTypeDict[edge[2]] and self.graphTypeDict[edge] != 0:
                    flagOptional = True
                elif self.graphTypeDict[edge] >= self.resourceTypeDict[edge[2]]:
                    flagOptional = False
                else:
                    continue
                
                type1 = edge[0].split(".")[0]
                ref1 = ".".join(edge[0].split(".")[1:])
                type2 = edge[1].split(".")[0]
                ref2 = ".".join(edge[1].split(".")[1:])
                if self.graphTypeDict[edge] > 10000:
                    additionalTuple.add((type2, ref2))
                for index1, resourceBlock1 in enumerate(plan):
                    resourceType1 = resourceBlock1["type"]
                    resourceName1 = resourceBlock1["address"]
                    if resourceType1 not in dependencyList:
                        continue
                    if resourceType1 == type1:
                        for index2, resourceBlock2 in enumerate(plan):
                            if index1 == index2:
                                continue
                            resourceType2 = resourceBlock2["type"]
                            resourceName2 = resourceBlock2["address"]
                            if resourceName2 == resourceName1:
                                continue
                            if resourceType2 not in dependencyList:
                                continue
                            if resourceType2 == type2:
                                self.outputSum[resourceName1].append(z3.If(self.directly_connected(self.vertexDict[resourceName1+"."+ref1], self.vertexDict[resourceName2+"."+ref2]), 1, 0))
                                self.outputSum[resourceName2].append(z3.If(self.directly_connected(self.vertexDict[resourceName1+"."+ref1], self.vertexDict[resourceName2+"."+ref2]), 1, 0))
                                if flagOptional == False:
                                    self.inputSum[f"{resourceName2}___{ref2}"].append(z3.If(self.directly_connected(self.vertexDict[resourceName1+"."+ref1], self.vertexDict[resourceName2+"."+ref2]), 1, 0))
            print("additionalTuple", additionalTuple)
            for _, resourceBlock in enumerate(plan):
                resourceType = resourceBlock["type"]
                resourceName = resourceBlock["address"]
                sum2 = z3.Int(f"{resourceName}_output")
                self.optimizer.add(sum2 == z3.Sum(self.outputSum[resourceName])) 
                for key in self.inputSum:
                    if f"{resourceName}___" in key:
                        sum1 = z3.Int(f"{key}_input")
                        self.optimizer.add(sum1 == z3.Sum(self.inputSum[key])) 
                        if purpose == "GEN" or purpose == "AGGTOPO" or purpose == "AGGATTR":
                            if (resourceType, key[len(f"{resourceName}___"):]) not in additionalTuple:
                                self.optimizer.add(z3.Or(z3.Not(sum2 >= 1), sum1 >= 1))
                            else:
                                self.optimizer.add(sum1 >= 1)
                            if key[-1] != "s":
                                self.optimizer.add(sum1 <= 1)
                            else:
                                self.optimizer.add_soft(sum1 <= 1)
                    
        ### declare type system for all nodes
        for entityName in self.instanceDict:
            entityType = self.instanceDict[entityName]
            self.optimizer.add(self.vertex_type(self.vertexDict[entityName], self.typeDict[entityType]))
            for resourceType in self.resourceTypeSet:
                if resourceType != entityType:
                    self.optimizer.add(z3.Not(self.vertex_type(self.vertexDict[entityName], self.typeDict[resourceType])))
        
        ### This is to make sure we don't accidentally add new edges for non-target rules.
        ### Also merged with the logic of obtaining resource and ancestor connectivity.
        sumAllConnection = z3.Int("all_connection_sum")
        allConnectionFormulas = []
        flagLoop = False
        for _, resourceBlock1 in enumerate(plan):
            for _, resourceBlock2 in enumerate(plan):
                resourceType1 = resourceBlock1["type"]
                resourceName1 = resourceBlock1["address"]
                resourceType2 = resourceBlock2["type"]
                resourceName2 = resourceBlock2["address"]
                if resourceName1 == resourceName2:
                    continue
                if resourceType1 not in dependencyList or resourceType2 not in dependencyList:
                    continue
                sum = z3.Int(f"{resourceName1}_{resourceName2}_connection_sum")
                formulas = []
                for type1, type2, ref1, ref2 in dependencyList[resourceType1]:
                    if type1 == type2:
                        if purpose in ["AGGTOPO", "AGGATTR"]:
                            continue
                    if resourceType2 == type2 and resourceType1 == type1:
                        resourcePort1 = resourceName1 + "." + ref1
                        resourcePort2 = resourceName2 + "." + ref2
                        flagMatter = False
                        for edge in self.graphTypeDict:
                            if type1 == edge[1].split(".")[0] and type2 == edge[0].split(".")[0]:
                                if ref1 == ".".join(edge[1].split(".")[1:]) and ref2 == ".".join(edge[0].split(".")[1:]):
                                    flagMatter = True
                                    break
                        if flagMatter == False:
                            self.optimizer.add(self.in_solution(self.vertexDict[resourcePort2], self.vertexDict[resourcePort1]) == False)
                        if "ZODIAC" in resourcePort2:
                            allConnectionFormulas.append(z3.If(self.in_solution(self.vertexDict[resourcePort2], self.vertexDict[resourcePort1]), 1, 0))
                        if "ZODIAC" in resourcePort1:
                            allConnectionFormulas.append(z3.If(self.in_solution(self.vertexDict[resourcePort2], self.vertexDict[resourcePort1]), 1, 0))
                        
                        if (resourceName1, resourceName2, resourcePort1, resourcePort2) not in self.dependencyPortSet:
                            if resourceName1 not in virtualResourceList and resourceName2 not in virtualResourceList:
                                self.optimizer.add(z3.Not(self.directly_connected(self.vertexDict[resourcePort2], self.vertexDict[resourcePort1])))
                            self.optimizer.add(z3.Not(self.given(self.vertexDict[resourcePort2], self.vertexDict[resourcePort1])))
                       
                        if resourceName1 not in virtualResourceList and resourceName2 not in virtualResourceList:
                            self.optimizer.add(
                                self.given(self.vertexDict[resourcePort2], self.vertexDict[resourcePort1]) ==
                                self.directly_connected(self.vertexDict[resourcePort2], self.vertexDict[resourcePort1])
                            )
                        else:
                            self.optimizer.add(
                                self.in_solution(self.vertexDict[resourcePort2], self.vertexDict[resourcePort1]) ==
                                self.directly_connected(self.vertexDict[resourcePort2], self.vertexDict[resourcePort1])
                            )
                        
                        formulas.append(z3.If(z3.And(self.directly_connected(self.vertexDict[resourcePort2], self.vertexDict[resourcePort1]) == True, 
                                            self.directly_connected(self.vertexDict[resourcePort1], self.vertexDict[resourceName1]) == True, \
                                            self.directly_connected(self.vertexDict[resourceName2], self.vertexDict[resourcePort2])) == True, 1, 0))

                self.optimizer.add(sum == z3.Sum(formulas))   
                self.optimizer.add(self.resource_connected(self.vertexDict[resourceName2], self.vertexDict[resourceName1]) == z3.If(sum >= 1, True, False))
                sum = z3.Int(f"{resourceName1}_{resourceName2}_two_hop_sum")
                formulas = []
                self.optimizer.add(z3.Implies(self.resource_connected(self.vertexDict[resourceName1], self.vertexDict[resourceName2]) == True, self.resource_connected(self.vertexDict[resourceName2], self.vertexDict[resourceName1]) == False))
                
                if resourceType2 == resourceType1:
                    continue
                if not resourceType1 in globalAncestorDict[resourceType2]:
                    continue
                formulas.append(z3.If(self.resource_connected(self.vertexDict[resourceName1], self.vertexDict[resourceName2]), 1, 0))
                    
                for  _, resourceBlock3 in enumerate(plan):
                    
                    resourceType3 = resourceBlock3["type"]
                    resourceName3 = resourceBlock3["address"]
                    if resourceType2 == resourceType1 or resourceType3 == resourceType1 or resourceType2 == resourceType3:
                        continue
                    if (not resourceType1 in globalAncestorDict[resourceType3]) or (not resourceType3 in globalAncestorDict[resourceType2]):
                        continue
                    else:
                        formulas.append(z3.If(z3.And(self.resource_connected(self.vertexDict[resourceName1], self.vertexDict[resourceName3]) == True, \
                                                     self.resource_connected(self.vertexDict[resourceName3], self.vertexDict[resourceName2]) == True), 1, 0))
                        formulas.append(z3.If(z3.And(self.ancestor_connected(self.vertexDict[resourceName1], self.vertexDict[resourceName3]) == True, \
                                                     self.resource_connected(self.vertexDict[resourceName3], self.vertexDict[resourceName2]) == True), 1, 0))
                self.optimizer.add(sum == z3.Sum(formulas))    
                self.optimizer.add(self.ancestor_connected(self.vertexDict[resourceName1], self.vertexDict[resourceName2]) == z3.If(sum >= 1, True, False))
                ### Makes sure we can avoid loops
                self.optimizer.add(z3.Implies(self.ancestor_connected(self.vertexDict[resourceName1], self.vertexDict[resourceName2]) == True, self.ancestor_connected(self.vertexDict[resourceName2], self.vertexDict[resourceName1]) == False))
        self.optimizer.add(sumAllConnection == z3.Sum(allConnectionFormulas))  
        self.countDict["SumAllConnection"] = sumAllConnection   
        
        for _, resourceBlock1 in enumerate(plan):
            resourceType1 = resourceBlock1["type"]
            resourceName1 = resourceBlock1["address"]
            self.optimizer.add(self.resource_connected(self.vertexDict[resourceName1], self.vertexDict[resourceName1]) == False)
    
    def generate_topology_binary_mutation(self, valueArray, startIndex, flagEssence):
        ### add mutation strategies for topology expressions that uses binary operators (e.g. connections, indegree)
        self.index = startIndex
        for nodeName1, nodeName2, portName1, portName2, relation, manifest in valueArray:
            if manifest == "Condition":
                conditionCount_index = z3.Int(f"conditionCount_{self.index}")
                self.conditionCount_list.append(conditionCount_index)
                self.countDict[f"conditionCount_{self.index}"] = conditionCount_index
                inputName = nodeName1+"."+portName1
                outputName = nodeName2+"."+portName2
                inputType = inputName.split(".")[0]
                outputType = outputName.split(".")[0]
                if flagEssence == True:
                    self.optimizer.add(z3.Sum(self.outputSum[nodeName1]) >= 1)
                if relation in ["Reference"]:
                    self.optimizer.add(conditionCount_index == z3.If(self.directly_connected(self.vertexDict[outputName], self.vertexDict[inputName]), 1, 0))
                elif relation in ["Negation"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_negation_condition_sum")
                    formulas = []
                    for vertex in self.vertexOutputPortDict:
                        if vertex.split(".")[0] == outputType and ".".join(vertex.split(".")[2:]) == portName2 and ".".join(vertex.split(".")[:2]) != nodeName1:
                            formulas.append(z3.If(self.directly_connected(self.vertexDict[vertex], self.vertexDict[inputName]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(conditionCount_index == z3.If(sum == 0, 1, 0))
                elif relation in ["Exclusive"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_exlcusive_condition_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        formulas.append(z3.If(self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[vertex]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(conditionCount_index == z3.If(z3.And(sum == 1, self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[nodeName1])), 1, 0))
                elif relation in ["ConflictChild"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_conflict_condition_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == inputType:
                            formulas.append(z3.If(self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[vertex]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(conditionCount_index == z3.If(z3.And(sum == 1, self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[nodeName1])), 1, 0))
                elif relation in ["AncestorReference"]:
                    self.optimizer.add_soft(z3.Not(self.ancestor_connected(self.vertexDict[nodeName2], self.vertexDict[nodeName1])))
                    self.optimizer.add(conditionCount_index == z3.If(self.ancestor_connected(self.vertexDict[nodeName2], self.vertexDict[nodeName1]), 1, 0))
                elif relation in ["AncestorConflictChild"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_ancestor_conflict_condition_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == inputType:
                            formulas.append(z3.If(z3.And(self.ancestor_connected(self.vertexDict[nodeName2], self.vertexDict[vertex]), self.vertex_type(self.vertexDict[vertex], self.typeDict[inputType])), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(conditionCount_index == z3.If(z3.And(sum == 1, self.ancestor_connected(self.vertexDict[nodeName2], self.vertexDict[nodeName1])), 1, 0))
                elif relation in ["AggParent"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_count_parent_condition_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == outputType:
                            formulas.append(z3.If(self.resource_connected(self.vertexDict[vertex], self.vertexDict[nodeName1]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(conditionCount_index == z3.If(z3.And(sum <= int(portName2), self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[nodeName1])), 1, 0))
                elif relation in ["AggChild"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_count_child_condition_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == inputType:
                            formulas.append(z3.If(self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[vertex]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(conditionCount_index == z3.If(z3.And(sum <= int(portName1), self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[nodeName1])), 1, 0))
            elif manifest == "Statement":
                statementCount_index = z3.Int(f"statementCount_{self.index}")
                self.statementCount_list.append(statementCount_index)
                self.countDict[f"statementCount_{self.index}"] = statementCount_index
                inputName = nodeName1+"."+portName1
                outputName = nodeName2+"."+portName2
                inputType = inputName.split(".")[0]
                outputType = outputName.split(".")[0]
                if flagEssence == True:
                    self.optimizer.add(z3.Sum(self.outputSum[nodeName1]) >= 1)
                if relation in ["Reference"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_reference_statement_sum")
                    formulas = []
                    for vertex in self.vertexOutputPortDict:
                        if vertex.split(".")[0] == outputType and ".".join(vertex.split(".")[2:]) == portName2 and ".".join(vertex.split(".")[:2]) != nodeName1:
                            formulas.append(z3.If(self.directly_connected(self.vertexDict[vertex], self.vertexDict[inputName]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(sum == 1, 1, 0))
                elif relation in ["Negation"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_negation_statement_sum")
                    formulas = []
                    for vertex in self.vertexOutputPortDict:
                        if vertex.split(".")[0] == outputType and ".".join(vertex.split(".")[2:]) == portName2 and ".".join(vertex.split(".")[:2]) != nodeName1:
                            formulas.append(z3.If(self.directly_connected(self.vertexDict[vertex], self.vertexDict[inputName]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(sum == 0, 1, 0))
                elif relation in ["Exclusive"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_exlcusive_statement_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        formulas.append(z3.If(self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[vertex]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(z3.And(sum == 1, self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[nodeName1])), 1, 0))
                elif relation in ["ConflictChild"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_conflict_statement_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == inputType:
                            formulas.append(z3.If(self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[vertex]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(sum == 1, 1, 0))
                elif relation in ["AncestorReference"]:
                    self.optimizer.add_soft(z3.Not(self.ancestor_connected(self.vertexDict[nodeName2], self.vertexDict[nodeName1])))
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_ancestor_reference_statement_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == outputType and ".".join(vertex.split(".")[:2]) != nodeName1:
                            formulas.append(z3.If(z3.And(self.ancestor_connected(self.vertexDict[vertex], self.vertexDict[nodeName1]), self.vertex_type(self.vertexDict[vertex], self.typeDict[inputType])), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(sum == 1, 1, 0))
                elif relation in ["AncestorConflictChild"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_ancestor_conflict_statement_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == inputType:
                            formulas.append(z3.If(z3.And(self.ancestor_connected(self.vertexDict[nodeName2], self.vertexDict[vertex]), self.vertex_type(self.vertexDict[vertex], self.typeDict[inputType])), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(z3.And(sum == 1, self.ancestor_connected(self.vertexDict[nodeName2], self.vertexDict[nodeName1])), 1, 0))
                elif relation in ["AggParent"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_count_parent_statement_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == outputType:
                            formulas.append(z3.If(self.resource_connected(self.vertexDict[vertex], self.vertexDict[nodeName1]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(sum <= int(portName2), 1, 0))
                elif relation in ["AggChild"]:
                    sum = z3.Int(f"{nodeName2}_{nodeName1}_{self.index}_count_child_statement_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == inputType:
                            formulas.append(z3.If(self.resource_connected(self.vertexDict[nodeName2], self.vertexDict[vertex]), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(sum <= int(portName1), 1, 0))
            else:
                print("Something went wrong, unable to parse SMT manifest topology binary!")
                return
            self.index += 1
    
    def generate_topology_ternary_mutation(self, valueArray, startIndex, flagEssence):
        ### add mutation strategies for topology expressions that uses ternary operators (e.g. coconnections, copaths)
        self.index = startIndex
        
        for nodeName1, nodeName2, nodeName3, nodeName4, portName1, portName2, portName3, portName4, relation, manifest in valueArray:
            if manifest == "Condition":
                conditionCount_index = z3.Int(f"conditionCount_{self.index}")
                self.conditionCount_list.append(conditionCount_index)
                self.countDict[f"conditionCount_{self.index}"] = conditionCount_index
                inputName1 = nodeName1+"."+portName1
                outputName1 = nodeName3+"."+portName3
                inputName2 = nodeName2+"."+portName2
                outputName2 = nodeName4+"."+portName4
                inputType = inputName1.split(".")[0]
                outputType = outputName1.split(".")[0]
                if flagEssence == True:
                    self.optimizer.add(z3.Sum(self.outputSum[nodeName1]) >= 1)
                    self.optimizer.add(z3.Sum(self.outputSum[nodeName2]) >= 1)
                
                if relation in ["Branch"] :
                    sum = z3.Int(f"{inputName1}_{inputName2}_{self.index}_branch_condition_sum")
                    formulas = []
                    formulas.append(z3.If(z3.And(self.directly_connected(self.vertexDict[outputName1], self.vertexDict[inputName1]), \
                                                    self.directly_connected(self.vertexDict[outputName2], self.vertexDict[inputName2]) \
                                                ), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(conditionCount_index == z3.If(sum == 1, 1, 0 ))
                elif relation in ["Associate"] :
                    sum = z3.Int(f"{inputName1}_{inputName2}_{self.index}_associate_condition_sum")
                    formulas = []
                    formulas.append(z3.If(z3.And(self.directly_connected(self.vertexDict[outputName1], self.vertexDict[inputName1]), \
                                                 self.directly_connected(self.vertexDict[outputName2], self.vertexDict[inputName2]) \
                                                ), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(conditionCount_index == z3.If(sum == 1, 1, 0 ))
                elif relation in ["AncestorBranch"] :
                    sum = z3.Int(f"{inputName1}_{inputName2}_{self.index}_ancestor_branch_condition_sum")
                    formulas = []
                    formulas.append(z3.If(z3.And(self.ancestor_connected(self.vertexDict[nodeName3], self.vertexDict[nodeName1]), \
                                                    self.ancestor_connected(self.vertexDict[nodeName4], self.vertexDict[nodeName2]) \
                                                ), 1, 0))
                    
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(conditionCount_index == z3.If(sum == 1, 1, 0 ))
                elif relation in ["AncestorAssociate"] :
                    sum = z3.Int(f"{inputName1}_{inputName2}_{self.index}_ancestor_associate_condition_sum")
                    formulas = []
                    formulas.append(z3.If(z3.And(self.ancestor_connected(self.vertexDict[nodeName3], self.vertexDict[nodeName1]), \
                                                    self.ancestor_connected(self.vertexDict[nodeName4], self.vertexDict[nodeName2]) \
                                                ), 1, 0))
                    
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(conditionCount_index == z3.If(sum >= 1, 1, 0 ))
                elif relation in ["Intra"]:
                    self.optimizer.add(conditionCount_index == z3.If(z3.And(self.directly_connected(self.vertexDict[outputName1], self.vertexDict[inputName1]), \
                                                                            self.directly_connected(self.vertexDict[outputName2], self.vertexDict[inputName2]) \
                                                                           ), 1, 0))
            elif manifest == "Statement":
                statementCount_index = z3.Int(f"statementCount_{self.index}")
                self.statementCount_list.append(statementCount_index)
                self.countDict[f"statementCount_{self.index}"] = statementCount_index
                inputName1 = nodeName1+"."+portName1
                outputName1 = nodeName3+"."+portName3
                inputName2 = nodeName2+"."+portName2
                outputName2 = nodeName4+"."+portName4
                inputType = inputName1.split(".")[0]
                outputType = outputName1.split(".")[0]
                if flagEssence == True:
                    self.optimizer.add(z3.Sum(self.outputSum[nodeName1]) >= 1)
                    self.optimizer.add(z3.Sum(self.outputSum[nodeName2]) >= 1)
                
                if relation in ["Branch"] :
                    sum = z3.Int(f"{inputName1}_{inputName2}_{self.index}_branch_condition_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == outputType:
                            formulas.append(z3.If(z3.And(self.directly_connected(self.vertexDict[vertex+"."+portName3], self.vertexDict[inputName1]), \
                                                         self.directly_connected(self.vertexDict[vertex+"."+portName4], self.vertexDict[inputName2]) \
                                                        ), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(sum == 1, 1, 0 ))
                elif relation in ["Associate"]:
                    sum = z3.Int(f"{inputName1}_{inputName2}_{self.index}_associate_statement_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == inputType and nodeName3 != nodeName4:
                            formulas.append(z3.If(z3.And(self.directly_connected(self.vertexDict[outputName1], self.vertexDict[vertex+"."+portName1]), \
                                                         self.directly_connected(self.vertexDict[outputName2], self.vertexDict[vertex+"."+portName2]) \
                                                        ), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(sum == 1, 1, 0 ))
                elif relation in ["AncestorBranch"] :
                    sum = z3.Int(f"{inputName1}_{inputName2}_{self.index}_ancestor_branch_statement_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == outputType :
                            formulas.append(z3.If(z3.And(self.ancestor_connected(self.vertexDict[vertex], self.vertexDict[nodeName1]), \
                                                        self.ancestor_connected(self.vertexDict[vertex], self.vertexDict[nodeName2]) \
                                                        ), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(sum == 1, 1, 0 ))
                elif relation in ["AncestorAssociate"]:
                    sum = z3.Int(f"{inputName1}_{inputName2}_{self.index}_ancestor_associate_condition_sum")
                    formulas = []
                    for vertex in self.vertexNodeDict:
                        if vertex.split(".")[0] == inputType and nodeName3 != nodeName4:
                            formulas.append(z3.If(z3.And(self.ancestor_connected(self.vertexDict[nodeName3], self.vertexDict[vertex]), \
                                                        self.ancestor_connected(self.vertexDict[nodeName4], self.vertexDict[vertex]) \
                                                        ), 1, 0))
                    self.optimizer.add(sum == z3.Sum(formulas))
                    self.optimizer.add(statementCount_index == z3.If(sum >= 1, 1, 0 ))
                elif relation in ["Intra"]:
                    self.optimizer.add(statementCount_index == z3.If(z3.And(self.directly_connected(self.vertexDict[outputName1], self.vertexDict[inputName1]), \
                                                                            self.directly_connected(self.vertexDict[outputName2], self.vertexDict[inputName2]) \
                                                                           ), 1, 0))
            else:
                print("Something went wrong, unable to parse SMT manifest topology ternary!")
                return
            self.index += 1
            
