### Main entry for SMT based mutation. This module takes IaC programs and
### candidate/validated rules and turn them into instrumented SMT formulas.
### a satisfiable model from the SMT formula represents the required mutations
### to turn a positive test case into a negative test case.
import sys
import os
sys.path.insert(0, '..')
sys.path.insert(0, '../ruleTemplateInstantiation')
import utils.utils as utils
import json
from utils.utils import *
from collections import defaultdict
import time
import SMTMaster
import copy
import knowledgeBaseConstruction.regoMVPGetKnowledgeBase as regoMVPGetKnowledgeBase

### The details w.r.t. extracting all possible rule match instances from configuration + rule set.
def csv2regoConversion(operation, row, rowIndex, plan, config, valueDict, topoDict, operationList, conflictResolver, purpose):
    if operation in ["Absence", "Existence", "Constant", "AbsenceComboUp", "ExistenceComboUp", \
                     "AbsenceComboDown", "ExistenceComboDown", "ConstantComboUp", "ConstantComboDown", \
                     "NonConstant", "NonConstantComboDown", "NonConstantComboUp", "CIDRRange"]:
        resourceType = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceAttr = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
        resourceValue = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        rowIndex += 1
        if operation in ["Absence", "Existence", "AbsenceComboUp", "ExistenceComboUp", "AbsenceComboDown", "ExistenceComboDown"]:
            if resourceType+"."+resourceAttr in conflictResolver and conflictResolver[resourceType+"."+resourceAttr] == "Constant":
                print("conflictResolving Existence")
                return rowIndex, None
            else:
                conflictResolver[resourceType+"."+resourceAttr] = "Existence"
        else:
            if resourceType+"."+resourceAttr in conflictResolver and conflictResolver[resourceType+"."+resourceAttr] == "Existence":
                print("conflictResolving Constant")
                return rowIndex, None
            else:
                conflictResolver[resourceType+"."+resourceAttr] = "Constant"
        for resourceBlock in plan:
            if resourceBlock["type"] == resourceType:
                resourceName = resourceBlock["address"]
                try:
                    if "." not in resourceAttr:
                        attributeValue = resourceBlock["values"][resourceAttr]
                    else:
                        resourceAttrList = resourceAttr.split(".")
                        if len(resourceAttrList) > 2:
                            return rowIndex, None
                        else:
                            attributeValue = resourceBlock["values"][resourceAttrList[0]][0][resourceAttrList[1]]
                except:
                    attributeValue = None
    
                if operation in ["Absence", "Existence", "AbsenceComboUp", "ExistenceComboUp", "AbsenceComboDown", "ExistenceComboDown"]:
                    if attributeValue == None or attributeValue == [] or attributeValue == {}:
                        attributeValue = "Absence"
                    else:
                        attributeValue = "Existence"
                    valueArray = [resourceName+"."+resourceAttr, attributeValue, resourceValue, operation]
                    if operation in ["Absence", "Existence"]:
                        valueDict[(resourceName, resourceName)].append(valueArray[:]) 
                    elif operation in ["AbsenceComboUp", "ExistenceComboUp"]:
                        for resourceBlock2 in plan:
                            resourceName2 = resourceBlock2["address"]
                            valueDict[(resourceName2, resourceName)].append(valueArray[:])
                    elif operation in ["AbsenceComboDown", "ExistenceComboDown"]:
                        for resourceBlock2 in plan:
                            resourceName2 = resourceBlock2["address"]
                            valueDict[(resourceName, resourceName2)].append(valueArray[:])
                elif operation in ["Constant", "ConstantComboUp", "ConstantComboDown"]:
                    if attributeValue == True:
                        attributeValue = "true"
                    elif attributeValue == False:
                        attributeValue = "false"
                    elif type(attributeValue) == int:
                        attributeValue = str(attributeValue)
                    elif attributeValue == None:
                        attributeValue = "null"
                        continue
                    valueArray = [resourceName+"."+resourceAttr, attributeValue, resourceValue, operation]
                    if operation in ["Constant"]:
                        valueDict[(resourceName, resourceName)].append(valueArray[:])
                    elif operation in ["ConstantComboUp"]:
                        for resourceBlock2 in plan:
                            resourceName2 = resourceBlock2["address"]
                            valueDict[(resourceName2, resourceName)].append(valueArray[:])
                    elif operation in ["ConstantComboDown"]:
                        for resourceBlock2 in plan:
                            resourceName2 = resourceBlock2["address"]
                            valueDict[(resourceName, resourceName2)].append(valueArray[:])
                elif operation in ["NonConstant", "NonConstantComboUp", "NonConstantComboDown"]:
                    if attributeValue == True:
                        attributeValue = "true"
                    elif attributeValue == False:
                        attributeValue = "false"
                    elif type(attributeValue) == int:
                        attributeValue = str(attributeValue)
                    elif attributeValue == None:
                        attributeValue = "null"
                        continue
                    valueArray = [resourceName+"."+resourceAttr, attributeValue, resourceValue, operation]
                    if operation in ["NonConstant"]:
                        valueDict[(resourceName, resourceName)].append(valueArray[:])
                    elif operation in ["NonConstantComboUp"]:
                        for resourceBlock2 in plan:
                            resourceName2 = resourceBlock2["address"]
                            valueDict[(resourceName2, resourceName)].append(valueArray[:])
                    elif operation in ["NonConstantComboDown"]:
                        for resourceBlock2 in plan:
                            resourceName2 = resourceBlock2["address"]
                            valueDict[(resourceName, resourceName2)].append(valueArray[:])
                elif operation in ["CIDRRange"]:
                    if type(attributeValue) == list:
                        attributeValue = attributeValue[0]
                    if attributeValue == None:
                        print("Something went wrong when trying to find attribute value in lists")
                        return rowIndex, valueDict
                    valueArray = [resourceName+"."+resourceAttr, attributeValue, resourceValue, operation]
                    valueDict[(resourceName, resourceName)].append(valueArray[:])
                    
    elif operation in ["Equal", "Unequal", "CIDRInclude", "CIDRExclude", "EqualCombo", "UnequalCombo", "CIDRIncludeCombo", "CIDRExcludeCombo", "BinConstantCombo"]:
        resourceType1 = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceAttr1 = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
        resourceValue1 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resourceType2 = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        resourceAttr2 = row[rowIndex+1][find_nth(row[rowIndex+1], ".", 1)+1:find_nth(row[rowIndex+1], "=", 1)-1]
        resourceValue2 = row[rowIndex+1][find_nth(row[rowIndex+1], "=", 2)+2:]
        rowIndex += 2
        if resourceType1+"."+resourceAttr1 in conflictResolver and conflictResolver[resourceType1+"."+resourceAttr1] == "Existence":
            print("conflictResolving Constant")
            return rowIndex, None
        else:
            conflictResolver[resourceType1+"."+resourceAttr1] = "Constant"
        if resourceType2+"."+resourceAttr2 in conflictResolver and conflictResolver[resourceType2+"."+resourceAttr2] == "Existence":
            print("conflictResolving Constant")
            return rowIndex, None
        else:
            conflictResolver[resourceType2+"."+resourceAttr2] = "Constant"
        for index1, resourceBlock1 in enumerate(plan):
            for index2, resourceBlock2 in enumerate(plan):
                if resourceBlock1["type"] != resourceType1 or resourceBlock2["type"] != resourceType2:
                    continue
                elif operation in ["Equal", "Unequal", "CIDRInclude", "CIDRExclude"] and index1 != index2:
                    continue
                elif operation in ["EqualCombo", "UnequalCombo", "CIDRIncludeCombo", "CIDRExcludeCombo", "BinConstantCombo"] and index1 == index2:
                    continue
                resourceName1 = resourceBlock1["address"]
                resourceName2 = resourceBlock2["address"]
                try:
                    if "." not in resourceAttr1:
                        attributeValue1 = resourceBlock1["values"][resourceAttr1]
                    else:
                        resourceAttrList1 = resourceAttr1.split(".")
                        if len(resourceAttrList1) > 2:
                            return rowIndex, None
                        else:
                            attributeValue1 = resourceBlock1["values"][resourceAttrList1[0]][0][resourceAttrList1[1]]
                    if "." not in resourceAttr2:
                        attributeValue2 = resourceBlock2["values"][resourceAttr2]
                    else:
                        resourceAttrList2 = resourceAttr2.split(".")
                        if len(resourceAttrList2) > 2:
                            return rowIndex, None
                        else:
                            if row[0] == "ATTR":
                                attributeValue2 = resourceBlock2["values"][resourceAttrList2[0]][1][resourceAttrList2[1]]
                            else: 
                                attributeValue2 = resourceBlock2["values"][resourceAttrList2[0]][0][resourceAttrList2[1]]
                except:
                    return rowIndex, None
                try:
                    if type(attributeValue1) == list:
                        attributeValue1 = attributeValue1[0]
                    if type(attributeValue2) == list:
                        attributeValue2 = attributeValue2[0]
                except:
                    print("Something went wrong when trying to find attribute value in empty lists", row)
                    return rowIndex, None
                if attributeValue1 == None or attributeValue2 == None:
                    return rowIndex, None
                if type(attributeValue1) == int:
                    attributeValue1 = str(attributeValue1)
                elif attributeValue1 == True:
                    attributeValue1 = "true"
                elif attributeValue1 == False:
                    attributeValue1 = "false"
                if type(attributeValue2) == int:
                    attributeValue2 = str(attributeValue2)
                elif attributeValue2 == True:
                    attributeValue2 = "true"
                elif attributeValue2 == False:
                    attributeValue2 = "false"
                if operation in ["Equal", "Unequal", "CIDRInclude", "CIDRExclude"]:
                    valueArray = [resourceName1+"."+resourceAttr1, attributeValue1, resourceName2+"."+resourceAttr2, attributeValue2, operation]
                    valueDict[(resourceName1, resourceName2)].append(valueArray[:])
                elif operation in ["EqualCombo", "UnequalCombo", "CIDRIncludeCombo", "CIDRExcludeCombo"]:
                    valueArray = [resourceName1+"."+resourceAttr1, attributeValue1, resourceName2+"."+resourceAttr2, attributeValue2, operation]
                    valueDict[(resourceName1, resourceName2)].append(valueArray[:])
                elif operation in ["BinConstantCombo"]:
                    valueArray = [resourceName1+"."+resourceAttr1, attributeValue1, resourceValue1, resourceName2+"."+resourceAttr2, attributeValue2, resourceValue1, operation]
                    valueDict[(resourceName1, resourceName2)].append(valueArray[:])

    elif operation in ["Reference", "Exclusive", "ConflictChild", "Negation", "AncestorReference", "AncestorConflictChild", "AggParent", "AggChild"]:
        resourceType1 = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceAttr1 = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
        resourceValue1 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resourceType2 = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        resourceAttr2 = row[rowIndex+1][find_nth(row[rowIndex+1], ".", 1)+1:find_nth(row[rowIndex+1], "=", 1)-1]
        resourceValue2 = row[rowIndex+1][find_nth(row[rowIndex+1], "=", 2)+2:]
        rowIndex += 2
        if operation in ["Reference", "AncestorReference"]:
            for index1, resourceBlock1 in enumerate(plan):
                for index2, resourceBlock2 in enumerate(plan):
                    if index1 == index2:
                        continue
                    if resourceBlock1["type"] != resourceType1 or resourceBlock2["type"] != resourceType2:
                        continue
                    resourceName1 = resourceBlock1["address"]
                    resourceName2 = resourceBlock2["address"]
                    nodeName1 = resourceName1
                    nodeName2 = resourceName2
                    portName1 = resourceAttr1
                    portName2 = resourceAttr2
                    valueArray = [nodeName1, nodeName2, portName1, portName2, operation]
                    valueDict[(resourceName1, resourceName2)].append(valueArray[:])
                    topoDict[(resourceName1, resourceName2)].append(valueArray[:])
        elif operation in ["Negation"]:
            for index1, resourceBlock1 in enumerate(plan):
                if resourceBlock1["type"] != resourceType1:
                    continue
                resourceName1 = resourceBlock1["address"]
                nodeName1 = resourceName1
                nodeName2 = resourceType2
                portName1 = resourceAttr1
                portName2 = resourceAttr2
                valueArray = [nodeName1, nodeName2, portName1, portName2, operation]
                valueDict[(resourceName1, resourceName1)].append(valueArray[:])
                topoDict[(resourceName1, resourceName1)].append(valueArray[:])
        elif operation in ["Exclusive"]:
            for index1, resourceBlock1 in enumerate(plan):
                for index2, resourceBlock2 in enumerate(plan):
                    if index1 == index2:
                        continue
                    if resourceBlock1["type"] != resourceType1 or resourceBlock2["type"] != resourceType2:
                        continue
                    resourceName1 = resourceBlock1["address"]
                    resourceName2 = resourceBlock2["address"]
                    nodeName1 = resourceName1
                    nodeName2 = resourceName2
                    portName1 = resourceAttr1
                    portName2 = resourceAttr2
                    valueArray = [nodeName1, nodeName2, portName1, portName2, operation]
                    valueDict[(resourceName1, resourceName2)].append(valueArray[:]) 
                    topoDict[(resourceName1, resourceName2)].append(valueArray[:])
        elif operation in ["ConflictChild", "AncestorConflictChild"]:
             for index1, resourceBlock1 in enumerate(plan):
                for index2, resourceBlock2 in enumerate(plan):
                    if index1 == index2:
                        continue
                    if resourceBlock1["type"] != resourceType1 or resourceBlock2["type"] != resourceType2:
                        continue
                    resourceName1 = resourceBlock1["address"]
                    resourceName2 = resourceBlock2["address"]
                    nodeName1 = resourceName1
                    nodeName2 = resourceName2
                    portName1 = resourceAttr1
                    portName2 = resourceAttr2
                    valueArray = [nodeName1, nodeName2, portName1, portName2, operation]
                    valueDict[(resourceName1, resourceName2)].append(valueArray[:]) 
                    topoDict[(resourceName1, resourceName2)].append(valueArray[:])
        elif operation in ["AggParent", "AggChild"]:
             for index1, resourceBlock1 in enumerate(plan):
                for index2, resourceBlock2 in enumerate(plan):
                    if index1 == index2:
                        continue
                    if resourceBlock1["type"] != resourceType1 or resourceBlock2["type"] != resourceType2:
                        continue
                    resourceName1 = resourceBlock1["address"]
                    resourceName2 = resourceBlock2["address"]
                    nodeName1 = resourceName1
                    nodeName2 = resourceName2
                    if purpose == "AGGTOPO":
                        portName1 = "1"
                        portName2 = "1"
                    else:
                        portName1 = resourceValue1
                        portName2 = resourceValue2
                    valueArray = [nodeName1, nodeName2, portName1, portName2, operation]
                    valueDict[(resourceName1, resourceName2)].append(valueArray[:]) 
                    topoDict[(resourceName1, resourceName2)].append(valueArray[:])
    elif operation in ["Branch", "Associate", "Intra", "AncestorBranch", "AncestorAssociate"]:
        resourceType1 = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceAttr1 = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
        resourceValue1 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resourceType2 = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        resourceAttr2 = row[rowIndex+1][find_nth(row[rowIndex+1], ".", 1)+1:find_nth(row[rowIndex+1], "=", 1)-1]
        resourceValue2 = row[rowIndex+1][find_nth(row[rowIndex+1], "=", 2)+2:]
        resourceType3 = row[rowIndex+2][:find_nth(row[rowIndex+2], ".", 1)]
        resourceAttr3 = row[rowIndex+2][find_nth(row[rowIndex+2], ".", 1)+1:find_nth(row[rowIndex+2], "=", 1)-1]
        resourceValue3 = row[rowIndex+2][find_nth(row[rowIndex+2], "=", 2)+2:]
        resourceType4 = row[rowIndex+3][:find_nth(row[rowIndex+3], ".", 1)]
        resourceAttr4 = row[rowIndex+3][find_nth(row[rowIndex+3], ".", 1)+1:find_nth(row[rowIndex+3], "=", 1)-1]
        resourceValue4 = row[rowIndex+3][find_nth(row[rowIndex+3], "=", 2)+2:]
        rowIndex += 4
        
        if operation in ["Branch", "AncestorBranch"]:
            for index1, resourceBlock1 in enumerate(plan):
                for index2, resourceBlock2 in enumerate(plan):
                    for index3, resourceBlock3 in enumerate(plan):
                        if resourceBlock1["type"] != resourceType1 or resourceBlock2["type"] != resourceType2 or resourceBlock3["type"] != resourceType3:
                            continue
                        if index1 >= index2 and resourceType1 == resourceType2:
                            continue
                        # if index1 >= index2:
                        #     continue
                        resourceName1 = resourceBlock1["address"]
                        resourceName2 = resourceBlock2["address"]
                        resourceName3 = resourceBlock3["address"]
                        nodeName1 = resourceName1
                        nodeName2 = resourceName2
                        nodeName3 = resourceName3
                        portName1 = resourceAttr1
                        portName2 = resourceAttr2
                        portName3 = resourceAttr3
                        portName4 = resourceAttr4
                        valueArray = [nodeName1, nodeName2, nodeName3, nodeName3, portName1, portName2, portName3, portName4, operation]
                        valueDict[(resourceName1, resourceName2, resourceName3)].append(valueArray[:])
                        topoDict[(resourceName1, resourceName2, resourceName3)].append(valueArray[:])
        elif operation in ["Associate", "AncestorAssociate"]:
            for index1, resourceBlock1 in enumerate(plan):
                for index3, resourceBlock3 in enumerate(plan):
                    for index4, resourceBlock4 in enumerate(plan):
                        if resourceBlock1["type"] != resourceType1 or resourceBlock3["type"] != resourceType3 or resourceBlock4["type"] != resourceType4:
                            continue
                        
                        if index3 >= index4 and resourceType3 == resourceType4:
                            continue
                        resourceName1 = resourceBlock1["address"]
                        resourceName3 = resourceBlock3["address"]
                        resourceName4 = resourceBlock4["address"]
                        nodeName1 = resourceName1
                        nodeName3 = resourceName3
                        nodeName4 = resourceName4
                        portName1 = resourceAttr1
                        portName2 = resourceAttr2
                        portName3 = resourceAttr3
                        portName4 = resourceAttr4
                        valueArray = [nodeName1, nodeName1, nodeName3, nodeName4, portName1, portName2, portName3, portName4, operation]
                        if operationList[0] in ["Reference"] or operationList[1] in ["Reference"]:
                            valueDict[(resourceName1, resourceName3, resourceName4)].append(valueArray[:])
                            topoDict[(resourceName1, resourceName3, resourceName4)].append(valueArray[:])
                        else:
                            valueDict[(resourceName3, resourceName4, resourceName1)].append(valueArray[:])
                            topoDict[(resourceName3, resourceName4, resourceName1)].append(valueArray[:])
        elif operation in ["Intra"]:
            for index1, resourceBlock1 in enumerate(plan):
                for index3, resourceBlock3 in enumerate(plan):
                    if resourceBlock1["type"] != resourceType1 or resourceBlock3["type"] != resourceType3:
                        continue
                    resourceName1 = resourceBlock1["address"]
                    resourceName3 = resourceBlock3["address"]
                    nodeName1 = resourceName1
                    nodeName3 = resourceName3
                    portName1 = resourceAttr1
                    portName2 = resourceAttr2
                    portName3 = resourceAttr3
                    portName4 = resourceAttr4
                    valueArray = [nodeName1, nodeName1, nodeName3, nodeName3, portName1, portName2, portName3, portName4, operation]
                    valueDict[(resourceName1, resourceName3)].append(valueArray[:])
                    topoDict[(resourceName1, resourceName3)].append(valueArray[:])
    
    return rowIndex, valueDict 

### Initiate necessary virtual resources. The type and amount of virtual resources is determined by
### the nature of topo/aggregate operators in the target rule statement. One question to consider is 
### how to treat cases where we need to do deletion rather than addition. It appears we can convert 
### all deletion cases into addition cases with ease: just force the shape among virtual resources!
def virtualResourceInit(resourceType, violationRow, plan, ancestorDict, inclusiveAncestorDict, referencesPredDict, purpose, \
                        MDCResources, typeMapping, globalTypeMapping, dependencyList, globalAncestorDict, globalSuccessorDict, resourceDependencyView, originalDependencyList):
    ### initiating virtual nodes based on the type of topology operators
    relatedResourceTypes = set()
    relatedResources = set()
    planFiltered = []
    planOriginal = []
    violationOperationList = violationRow[1].split("If")
    violationOperationList = violationOperationList[0].split("Then")
    virtualResourceDict = defaultdict(list)
    waivedSet = set()
    additionalGraphTypeDict = defaultdict(int)
    new2oldMapping = defaultdict()
    removedEdges = []
    additionalResource = defaultdict()
    ignoredResourceSet = set()
    
    ### Make sure we only consider resources that we can safely handle. Others should all be discarded.
    if purpose == "MDC":
        planFiltered = []
        planOriginal = []
            
        for resourceBlock1 in plan[:]:
            resourceBlockType1 = resourceBlock1["type"]
            resourceBlockName1 = resourceBlock1["address"]
            if resourceBlockType1 == resourceType:
                if resourceBlockName1 not in inclusiveAncestorDict:
                    continue
                for ancestorResourceName in inclusiveAncestorDict[resourceBlockName1]:
                    ### load ancestors regardless of whether under control of zodiac
                    ancestorResourceType = ancestorResourceName.split(".")[0]
                    
                    for resourceBlock2 in plan[:]:
                        resourceBlockName2 = resourceBlock2["address"] 
                        if resourceBlockName2 == ancestorResourceName:
                            if ancestorResourceType in regoMVPGetKnowledgeBase.resourceList:
                                if resourceBlock2 not in planFiltered:
                                    planFiltered.append(resourceBlock2)
                            else:
                                if resourceBlock2 not in planOriginal:
                                    planOriginal.append(resourceBlock2)
        print("MDC evaluation related number of resources: ", len(planFiltered))
        return plan, planFiltered, planOriginal, waivedSet, virtualResourceDict, new2oldMapping, additionalGraphTypeDict, additionalResource, 0, relatedResourceTypes, dependencyList, removedEdges, originalDependencyList, ignoredResourceSet

    elif purpose == "AGGATTR":
        planFiltered = MDCResources["planFiltered"]
        realvNodeCount = int(MDCResources["vNodeCount"])
        usedVirtualResources = set()
        for outputPort, inputPort in MDCResources["dependency"]:
            inputResourceType = inputPort.split(".")[0]
            inputResourceName = inputPort.split(".")[1]
            outputResourceType = outputPort.split(".")[0]
            outputResourceName = outputPort.split(".")[1]
            if "ZODIAC" in inputResourceName:
                usedVirtualResources.add(inputResourceType + "." + inputResourceName)
            if "ZODIAC" in outputResourceName:
                usedVirtualResources.add(outputResourceType + "." + outputResourceName)
        planExaming = planFiltered[:]
        planFiltered = []
        for resourceBlock in planExaming:
            if "ZODIAC-" in resourceBlock["address"]:
                if resourceBlock["address"] in usedVirtualResources:
                    for index in range(0,realvNodeCount):
                        resourceBlockNew = copy.deepcopy(resourceBlock)
                        resourceBlockNew["address"] = resourceBlockNew["address"][:-2]+"-"+str(index)
                        planFiltered.append(resourceBlockNew)
            else:
                planFiltered.append(resourceBlock)
        for element in  planFiltered:
            print("element:", element)
        planOriginal = MDCResources["planOriginal"]
        new2oldMapping = MDCResources["mapping"]
        print("new2oldMapping", new2oldMapping)
        for newAddress in list(new2oldMapping.keys()):
            oldAddress = new2oldMapping[newAddress]
            if "ZODIAC-" in newAddress:
                for index in range(1,realvNodeCount):
                    interAddress = newAddress[:-2]+"-"+str(index)
                    new2oldMapping[interAddress] = oldAddress
        print("AGGATTR evaluation related number of resources: ", len(planFiltered))
        return plan, planFiltered, planOriginal, waivedSet, virtualResourceDict, new2oldMapping, additionalGraphTypeDict, additionalResource, 0, relatedResourceTypes, dependencyList, removedEdges, originalDependencyList, ignoredResourceSet
    
    filteredResources = [] 
    print("GEN evaluation related Resources: ", MDCResources["MDC"])
    for resourceName in MDCResources["MDC"]:
        for ancestorResource in ancestorDict[resourceName]:
            filteredResources.append(ancestorResource)
            ancestorType = ancestorResource.split(".")[0]
            if ancestorType not in relatedResourceTypes:
                relatedResourceTypes.add(ancestorType)
                relatedResources.add(ancestorResource)
        
    print("relatedResources: ", relatedResources)
    print("relatedResourceTypes: ", relatedResourceTypes)
    
    ### Handle GEN/ATTRTOPO virtual nodes generation (core logic)
    vNodeCount = 0
    planOriginal = MDCResources["planOriginal"]
    if purpose != "AGGATTR" and violationOperationList[-1] in ["Branch", "ConflictChild", "AncestorBranch", "AncestorConflictChild", \
                                                               "AggParent", "AggChild", "Reference", "AncestorReference", "Associate", "AncestorAssociate", "Intra"]:
        if violationOperationList[-1] in ["Branch", "AncestorBranch"]:
            vNodeCount = 1
            tempDependencyList = dependencyList[:]
            dependencyList = []
            removeSource = set()
            removeEdgeType = set()
            for oldNode1, oldNode2, oldPort1, oldPort2, oldSlice1, oldSlice2 in tempDependencyList:
                if (len(removeSource) == 0 or oldNode2.split(".")[0] in removeSource)  and oldNode2.split(".")[0] == violationRow[-1][:find_nth(violationRow[-1], ".", 1)]:
                    removeSource.add(oldNode2.split(".")[0])
                    print(oldNode1.split(".")[0], globalAncestorDict[violationRow[-3][:find_nth(violationRow[-3], ".", 1)]])
                    if (oldNode2.split(".")[0], oldNode1.split(".")[0]) not in removeEdgeType and \
                        oldNode2 in filteredResources and oldNode1 in filteredResources and \
                       (oldNode1.split(".")[0] in globalAncestorDict[violationRow[-3][:find_nth(violationRow[-3], ".", 1)]] or \
                        oldNode1.split(".")[0] == violationRow[-3][:find_nth(violationRow[-3], ".", 1)]):
                        removeEdgeType.add((oldNode2.split(".")[0], oldNode1.split(".")[0]))
                        removedEdges.append([oldNode1, oldNode2, oldPort1, oldPort2, oldSlice1, oldSlice2])
                    else:
                        dependencyList.append([oldNode1, oldNode2, oldPort1, oldPort2, oldSlice1, oldSlice2])
                else:
                    dependencyList.append([oldNode1, oldNode2, oldPort1, oldPort2, oldSlice1, oldSlice2])
            resourceTypeTemp1 = violationRow[-3][:find_nth(violationRow[-3], ".", 1)]
            resourceTypeTemp2 = violationRow[2][:find_nth(violationRow[2], ".", 1)]
            waivedSet.add(resourceTypeTemp1)
            waivedSet.add(resourceTypeTemp2)
            print("removedEdges: ", removedEdges)
        elif violationOperationList[-1] in ["ConflictChild", "AncestorConflictChild"]:
            vNodeCount = 1
            resourceTypeTemp = violationRow[-1][:find_nth(violationRow[-1], ".", 1)]
            waivedSet.add(resourceTypeTemp)
        elif violationOperationList[-1] in ["Reference", "AncestorReference"]:
            vNodeCount = 2
            resourceTypeOutput = violationRow[-1][:find_nth(violationRow[-1], ".", 1)]
            resourceAttrOutput = violationRow[-1][find_nth(violationRow[-1], ".", 1)+1:find_nth(violationRow[-1], "=", 1)-1]
            resourceTypeInput = violationRow[-2][:find_nth(violationRow[-2], ".", 1)]
            resourceAttrInput = violationRow[-2][find_nth(violationRow[-2], ".", 1)+1:find_nth(violationRow[-2], "=", 1)-1]
            additionalGraphTypeDict[(resourceTypeOutput+"."+resourceAttrOutput, resourceTypeInput+"."+resourceAttrInput, resourceTypeInput)] -= 10000000
        elif violationOperationList[-1] in ["Associate", "AncestorAssociate", "Intra"]:
            vNodeCount = 2
            tempDependencyList = dependencyList[:]
        elif violationOperationList[-1] in ["AggParent"]:
            resourceTypeTemp = violationRow[-2][:find_nth(violationRow[-2], ".", 1)]
            waivedSet.add(resourceTypeTemp)
            vNodeCount = int(violationRow[-1][find_nth(violationRow[-1], "=", 2)+2:])
            if resourceType in ["azurerm_virtual_network_gateway"]:
                additionalGraphTypeDict[("azurerm_public_ip.id", "azurerm_virtual_network_gateway.ip_configuration.1.public_ip_address_id", "azurerm_virtual_network_gateway")] += 10000000
                additionalGraphTypeDict[("azurerm_public_ip.id", "azurerm_virtual_network_gateway.ip_configuration.2.public_ip_address_id", "azurerm_virtual_network_gateway")] += 10000000
                additionalGraphTypeDict[("azurerm_subnet.id", "azurerm_virtual_network_gateway.ip_configuration.1.subnet_id", "azurerm_virtual_network_gateway")] += 10000000
                additionalGraphTypeDict[("azurerm_subnet.id", "azurerm_virtual_network_gateway.ip_configuration.2.subnet_id", "azurerm_virtual_network_gateway")] += 10000000
        elif violationOperationList[-1] in ["AggChild"]:
            resourceTypeTemp = violationRow[-1][:find_nth(violationRow[-1], ".", 1)]
            waivedSet.add(resourceTypeTemp)
            vNodeCount = int(violationRow[-2][find_nth(violationRow[-2], "=", 2)+2:])
        print("virtual node count: ", vNodeCount)   
        
        for resourceBlock in plan[:]:
            resourceBlockType = resourceBlock["type"]
            resourceBlockName = resourceBlock["address"]
            # FIX ME: how to balance existing v.s. virtual nodes?
            if violationOperationList[-1] in ["AggParent", "AggChild", "ConflictChild", "AncestorConflictChild", "Branch", "AncestorBranch"]:
                if resourceBlockName in filteredResources:
                    planFiltered.append(resourceBlock)
                    new2oldMapping[resourceBlock["address"]] = resourceBlock["address"]
            else:
                if resourceBlockName in filteredResources:
                    ignoredResourceSet.add(resourceBlock["address"])
            if resourceBlockName in relatedResources:
                originalName = resourceBlock["name"]
                if resourceBlockType in waivedSet:
                    realvNodeCount = 0
                elif purpose == "AGGTOPO":
                    realvNodeCount = 1
                else:
                    realvNodeCount = vNodeCount
                for index in range(realvNodeCount):
                    resourceBlockNew = copy.deepcopy(resourceBlock)
                    resourceBlockNew["address"] = f"{resourceBlockType}.ZODIAC-{originalName}-{index}"
                    virtualResourceDict[index].append(resourceBlockNew["address"])
                    planFiltered.append(resourceBlockNew)
                    new2oldMapping[f"{resourceBlockType}.ZODIAC-{originalName}-{index}"] = resourceBlock["address"]
                    
    elif purpose != "AGGATTR" and violationOperationList[-1] in ["Negation", "Exclusive"]:
        resourceTypeOutput = violationRow[-1][:find_nth(violationRow[-1], ".", 1)]
        resourceAttrOutput = violationRow[-1][find_nth(violationRow[-1], ".", 1)+1:find_nth(violationRow[-1], "=", 1)-1]
        resourceTypeInput = violationRow[-2][:find_nth(violationRow[-2], ".", 1)]
        resourceAttrInput = violationRow[-2][find_nth(violationRow[-2], ".", 1)+1:find_nth(violationRow[-2], "=", 1)-1]
        for resourceBlock in plan[:]:
            resourceBlockType = resourceBlock["type"]
            resourceBlockName = resourceBlock["address"]
            if resourceBlockName in filteredResources:
                planFiltered.append(resourceBlock)
                new2oldMapping[resourceBlock["address"]] = resourceBlock["address"]
        if violationOperationList[-1] in ["Negation"]:
            resourceAttrMissing = resourceAttrOutput
            resourceTypeMissing = resourceTypeOutput
            resourceTypeExisting = resourceTypeInput
        elif violationOperationList[-1] in ["Exclusive"]:
            for resourceTypeTemp in globalSuccessorDict[resourceTypeOutput]:
                resourceTypeMissing = resourceTypeTemp
                resourceTypeExisting = resourceTypeOutput
                for type1, type2, attr1, attr2 in resourceDependencyView[resourceTypeMissing]:
                    if type1 == resourceTypeMissing and type2 == resourceTypeOutput:
                        resourceAttrMissing = attr1
                        resourceAttrOutput = attr2
                        break
                if resourceTypeTemp != resourceTypeInput and "associate" not in resourceTypeTemp and "attachment" not in resourceTypeTemp:
                    break
        missingMappingDict, missingDependencyListData = None, None
        missingMappingDirectory, missingKnowledgeDirectory = "", ""
        tempminLen = 10000
        for tempIndex in range(len(globalTypeMapping[resourceTypeMissing])):
            if "usageExample" not in globalTypeMapping[resourceTypeMissing][tempIndex][2]:
                continue
            tempmissingMappingDirectory = f"../folderFiles/folders_{resourceTypeMissing}_mapping/" + globalTypeMapping[resourceTypeMissing][tempIndex][2]
            tempmissingKnowledgeDirectory = f"../folderFiles/folders_{resourceTypeMissing}_knowledge/" + globalTypeMapping[resourceTypeMissing][tempIndex][2]
            tempmissingMappingDict = json.load(open(f"{tempmissingMappingDirectory}/mapping.json", "r"))
            tempmissingDependencyListData = json.load(open(f"{tempmissingKnowledgeDirectory}/dependencyList.json", "r"))
            flagExisting = False
            for resourceKey in tempmissingMappingDict:
                if resourceKey.split(".")[0] == resourceTypeExisting:
                    flagExisting = True
                    break
            if flagExisting == True:
                continue
            elif tempminLen > len(tempmissingMappingDict):
                tempminLen = len(tempmissingMappingDict)
                missingMappingDict, missingDependencyListData = tempmissingMappingDict, tempmissingDependencyListData
                missingMappingDirectory, missingKnowledgeDirectory = tempmissingMappingDirectory, tempmissingKnowledgeDirectory
        missingDependencyList = missingDependencyListData["result"][0]["expressions"][0]["value"]
        print(missingMappingDirectory)
        
        tempIndex = 0
        globalAncestorDict[resourceTypeMissing].append(resourceTypeMissing)
        tempResourceMapping = defaultdict()
        for resourceKey in missingMappingDict:
            missingResourcePlan = missingMappingDict[resourceKey][0]
            missingResourceBlock = missingMappingDict[resourceKey][1]
            tempResourceType = missingResourcePlan["type"]
            plan.append(missingResourcePlan)
            if tempResourceType not in regoMVPGetKnowledgeBase.resourceList:
                planOriginal.append(missingResourcePlan)
                additionalResource[missingResourcePlan["address"]] = [missingResourcePlan, missingResourceBlock]
                continue
            elif tempResourceType not in globalAncestorDict[resourceTypeMissing]:
                continue
            elif tempResourceType == resourceTypeMissing:
                pass
            elif tempResourceType != "azurerm_image":
                planOriginal.append(missingResourcePlan)
                additionalResource[missingResourcePlan["address"]] = [missingResourcePlan, missingResourceBlock]
            
            tempResourceMapping[missingResourcePlan["address"]] = f"{tempResourceType}.ZODIAC-Negation-{tempIndex}"
            missingResourcePlan["address"] = f"{tempResourceType}.ZODIAC-Negation-{tempIndex}"
            missingResourcePlan["name"] = f"ZODIAC-Negation-{tempIndex}"
            virtualResourceDict[0].append(missingResourcePlan["address"])
            planFiltered.append(missingResourcePlan)
            additionalResource[f"{tempResourceType}.ZODIAC-Negation-{tempIndex}"] = [missingResourcePlan, missingResourceBlock]
            new2oldMapping[missingResourcePlan["address"]] = missingResourcePlan["address"]
            tempIndex += 1
        
        for tempEdge in missingDependencyList:
            if tempEdge[0].split(".")[0] not in globalAncestorDict[resourceTypeMissing] or \
               tempEdge[1].split(".")[0] not in globalAncestorDict[resourceTypeMissing]:
                   continue
            else:
                originalDependencyList += [tempEdge]
                
        if violationOperationList[-1] in ["Negation"]:
            additionalGraphTypeDict[(resourceTypeMissing+"."+resourceAttrMissing, resourceTypeInput+"."+resourceAttrInput, resourceTypeInput)] += 10000000
        elif violationOperationList[-1] in ["Exclusive"]:
            additionalGraphTypeDict[(resourceTypeOutput+"."+resourceAttrOutput, resourceTypeMissing+"."+resourceAttrMissing, resourceTypeMissing)] += 10000000
    
    else:
        for resourceBlock in plan[:]:
            resourceBlockType = resourceBlock["type"]
            resourceBlockName = resourceBlock["address"]
            if resourceBlockName in filteredResources:
                planFiltered.append(resourceBlock)
                new2oldMapping[resourceBlock["address"]] = resourceBlock["address"]
                
    print("Instrumented number of resources: ", len(planFiltered))
    
    return plan, planFiltered, planOriginal, waivedSet, virtualResourceDict, new2oldMapping, additionalGraphTypeDict, additionalResource, vNodeCount, relatedResourceTypes, dependencyList, removedEdges, originalDependencyList, ignoredResourceSet

### Analyze SMT solving result when the purpose is to do negative test case generation. It should retrieve the 
### following information: 1. What resources need to be added/deleted. 2. What edges need to be added or deleted
### 3. What attributes need to be added or deleted. These information should then be fed into the postprocessing
### so that we can construct the actual mutated configurations that are ready to be deployed. 
def analyzeSMTGENResult(modelPerIndex, smtFormula, violationDetailDict, planFiltered, resourceDependencyView, testRule, violationRow, sumDict, resultDict, new2oldMapping, additionalResource, purpose, MDCResources):
    ### Capture confiuration changes calculated by smt solver
    violatedRules = set()
    tempCIDRDict = defaultdict(list)
    for newValueKey in modelPerIndex:
        if "_111_value" in str(newValueKey):
            oldValueKey = str(newValueKey)[:-6]
            newValue = str(modelPerIndex[newValueKey])[1:-1]
            oldValue = smtFormula.oldAttrValueDict[oldValueKey]
            if newValue != oldValue:
                print("Attribute value change: ", oldValueKey, newValue, oldValue)
                resultDict["attribute"].append([oldValueKey[:-4], newValue, oldValue, 1])
        elif "_value" in str(newValueKey):
            oldValueKey = str(newValueKey)[:-6]
            newValue = str(modelPerIndex[newValueKey])[1:-1]
            oldValue = smtFormula.oldAttrValueDict[oldValueKey]
            if newValue != oldValue:
                print("Attribute value change: ", oldValueKey, newValue, oldValue)
                resultDict["attribute"].append([oldValueKey, newValue, oldValue, 0])
        elif "_111_bv" in str(newValueKey):
            oldValueKey = str(newValueKey)[:-3]
            oldValue = smtFormula.oldAttrValueDict[oldValueKey]
            if oldValueKey in tempCIDRDict and len(tempCIDRDict[oldValueKey]) == 1:
                newValue = bv_to_ip(modelPerIndex[newValueKey])+"/"+tempCIDRDict[oldValueKey][0]
                if newValue != oldValue:
                    print("Attribute CIDR change: ", oldValueKey, newValue, oldValue)
                    resultDict["attribute"].append([oldValueKey[:-4], newValue, oldValue, 1])
            tempCIDRDict[oldValueKey].append(bv_to_ip(modelPerIndex[newValueKey]))
        elif "_bv" in str(newValueKey):
            oldValueKey = str(newValueKey)[:-3]
            oldValue = smtFormula.oldAttrValueDict[oldValueKey]
            if oldValueKey in tempCIDRDict and len(tempCIDRDict[oldValueKey]) == 1:
                newValue = bv_to_ip(modelPerIndex[newValueKey])+"/"+tempCIDRDict[oldValueKey][0]
                if newValue != oldValue:
                    print("Attribute CIDR change: ", oldValueKey, newValue, oldValue)
                    resultDict["attribute"].append([oldValueKey, newValue, oldValue, 0])
            tempCIDRDict[oldValueKey].append(bv_to_ip(modelPerIndex[newValueKey]))
        elif "_111_len" in str(newValueKey):
            oldValueKey = str(newValueKey)[:-4]
            oldValue = smtFormula.oldAttrValueDict[oldValueKey]
            if oldValueKey in tempCIDRDict and len(tempCIDRDict[oldValueKey]) == 1:
                newValue = tempCIDRDict[oldValueKey][0] + "/" + str(modelPerIndex[newValueKey])
                if newValue != oldValue:
                    print("Attribute CIDR change: ", oldValueKey, newValue, oldValue)
                    resultDict["attribute"].append([oldValueKey[:-4], newValue, oldValue, 1])
            tempCIDRDict[oldValueKey].append(str(modelPerIndex[newValueKey]))   
        elif "_len" in str(newValueKey):
            oldValueKey = str(newValueKey)[:-4]
            oldValue = smtFormula.oldAttrValueDict[oldValueKey]
            if oldValueKey in tempCIDRDict and len(tempCIDRDict[oldValueKey]) == 1:
                newValue = tempCIDRDict[oldValueKey][0] + "/" + str(modelPerIndex[newValueKey])
                if newValue != oldValue:
                    print("Attribute CIDR change: ", oldValueKey, newValue, oldValue)
                    resultDict["attribute"].append([oldValueKey, newValue, oldValue, 0])
            tempCIDRDict[oldValueKey].append(str(modelPerIndex[newValueKey]))
        elif "violationCount_" in str(newValueKey):
            oldValueKey = str(newValueKey)
            if int(str(modelPerIndex[newValueKey])) == 1:
                print("Violation details: ", oldValueKey, str(modelPerIndex[newValueKey]), violationDetailDict[oldValueKey][0])
                violatedRules.add(violationDetailDict[oldValueKey][1])
            
        elif "in_solution" in str(newValueKey):
            print("in_solution function: ", modelPerIndex[newValueKey])
        
            
    resultDict["mapping"] = new2oldMapping
    resultDict["additional"] = additionalResource
    resultDict["dependencyView"] = resourceDependencyView
    for _, resourceBlock1 in enumerate(planFiltered):
        resourceName1 = resourceBlock1["address"]
        resourceType1 = resourceBlock1["type"]
        for _, type2, ref1, ref2 in resourceDependencyView[resourceType1]:
            for _, resourceBlock2 in enumerate(planFiltered):
                resourceName2 = resourceBlock2["address"]
                resourceType2 = resourceBlock2["type"]
                try:
                    if resourceType2 == type2:
                        connectionResult = str(modelPerIndex.evaluate(smtFormula.in_solution(smtFormula.vertexDict[resourceName2+"."+ref2], smtFormula.vertexDict[resourceName1+"."+ref1])))
                        if connectionResult == "True":
                            print("Topology change: ", [resourceName2+"."+ref2, resourceName1+"."+ref1])
                            resultDict["dependency"].append([resourceName2+"."+ref2, resourceName1+"."+ref1])
                except Exception as e:
                    pass
                    #print("Something went wrong when trying to retrieve dependency changes", e)
    for violatedRule in violatedRules:
        if violatedRule == tuple(testRule):
            print("Primary violated rule: ", violatedRule)
        else:
            print("Other violated rule: ", violatedRule)
    resultDict["planFiltered"] = planFiltered
    if purpose == "AGGATTR":
        resultDict["dependency"] = MDCResources["dependency"]
    resultDict["violations"] = violatedRules
    print(f"Minimum total violations for {violationRow}: ", "attribute violations: ", modelPerIndex[sumDict["Sum"]], "topology violations: ", modelPerIndex[sumDict["SumTOPO"]], "attribute changes: ", modelPerIndex[sumDict["Changed"]], "name changes: ", modelPerIndex[sumDict["ChangedNAME"]])
    return resultDict

def analyzeSMTMDCResult(modelPerIndex, violationDetailDict, resultDict, violationRow, globalSuccessorDict, resourceDependencyView, planFiltered):
    flagMDC = False
    resultDict["flag"] = False
    for newValueKey in modelPerIndex:
        if "violationCount_" in str(newValueKey):
            oldValueKey = str(newValueKey)
            print("Violation count each: ", oldValueKey, str(modelPerIndex[newValueKey]), violationDetailDict[oldValueKey][0])
            if int(str(modelPerIndex[newValueKey])) == 1 and flagMDC == False:
                flagMDC = True
                resultDict["flag"] = True
                print("Violation count details: ", oldValueKey, str(modelPerIndex[newValueKey]), violationDetailDict[oldValueKey][0])
                for valueArray in violationDetailDict[oldValueKey][0]:
                    for valueItem in valueArray:
                        if "azurerm" == valueItem[:7] or "google" == valueItem[:6] or "aws" == valueItem[:3]:
                            resourceName = ".".join(valueItem.split(".")[:2])
                            if resourceName not in resultDict["MDC"] and "." in resourceName:
                                resultDict["MDC"].append(resourceName)
                                
        elif "in_solution" in str(newValueKey):
            print("in_solution function: ", modelPerIndex[newValueKey])
    
    return resultDict

### analyze candidate/validated/target rules and retrieve all possible rule match instances. Note thst
### these rule match instances may not all hold in the old/new configuration, but they MIGHT play a role
### so they should always be considered with in the SMT solving phase.
def getValueDict(operationList, row, planFiltered, config, conflictResolver, purpose):
    rowIndex = 2
    valueDict = defaultdict(list)
    topoDict1, topoDict2 = defaultdict(list), defaultdict(list)
    flagHandled = True
    for operation in operationList:
        if operation not in ["Absence", "Existence", "Constant", "Equal", "Unequal", "CIDRInclude", "CIDRExclude", \
                            "EqualCombo", "UnequalCombo", "CIDRIncludeCombo", "CIDRExcludeCombo", "AbsenceComboUp", "ExistenceComboUp", \
                            "AbsenceComboDown", "ExistenceComboDown", "ConstantComboUp", "ConstantComboDown", "BinConstantCombo", \
                            "Reference", "Branch", "Associate", "Exclusive", "ConflictChild", "Intra", "Negation", \
                            "AncestorReference", "AncestorConflictChild", "AncestorBranch", "AncestorAssociate", "AggParent", "AggChild", \
                            "NonConstant", "NonConstantComboDown", "NonConstantComboUp", "CIDRRange"]:
            flagHandled = False
            break
        if rowIndex == 2:
            rowIndex, valueDict = csv2regoConversion(operation, row, rowIndex, planFiltered, config, valueDict, topoDict1, operationList, conflictResolver, purpose)
            if valueDict == None:
                return None
        else:
            rowIndex, valueDict = csv2regoConversion(operation, row, rowIndex, planFiltered, config, valueDict, topoDict2, operationList, conflictResolver, purpose)
            if valueDict == None:
                return None
            
    if flagHandled == False:
        return valueDict
    valueSet = list(valueDict.keys())
    if operationList[0] in ["Reference", "Branch", "Associate", "Exclusive", "ConflictChild", "Intra", "Negation", \
                            "AncestorReference", "AncestorConflictChild", "AncestorBranch", "AncestorAssociate", "AggParent", "AggChild"] and \
        operationList[1] in ["Reference", "Branch", "Associate", "Exclusive", "ConflictChild", "Intra", "Negation", \
                            "AncestorReference", "AncestorConflictChild", "AncestorBranch", "AncestorAssociate", "AggParent", "AggChild"]:
        ### Handling TOPO combinations, so that we can process cases where both condition and statement are TOPO operators.
        valueDict = defaultdict(list)
        keyIndex = 0 
        tempSet = set()
        for key1 in list(topoDict1.keys()):
            for key2 in list(topoDict2.keys()):
                if "Negation" in operationList:
                    if key1[:1] == key2[:1]:
                        keyIndex += 1
                        valueDict[keyIndex] = topoDict1[key1][:] + topoDict2[key2][:]
                elif operationList[0] in ["Branch", "Associate", "AncestorBranch", "AncestorAssociate", "Intra"]:
                    if key1[:2] == key2[:2] and tuple(key1[:3]) not in tempSet:
                        keyIndex += 1
                        valueDict[keyIndex] = topoDict1[key1][:] + topoDict2[key2][:]
                        tempSet.add(tuple(key1[:3]))
                else:
                    if key1[:2] == key2[:2] and tuple(key1[:2]) not in tempSet:
                        keyIndex += 1
                        valueDict[keyIndex] = topoDict1[key1][:] + topoDict2[key2][:]
                        tempSet.add(tuple(key1[:2]))
    elif operationList[0] in ["Branch", "Associate", "AncestorBranch", "AncestorAssociate"] or operationList[1] in ["Branch", "Associate", "AncestorBranch", "AncestorAssociate"]:
        ### Handling COMBO ternary operators, so that there is no ambiguity on the third operator
        for valueKey1 in valueSet:
            if len(valueKey1) == 3:
                for valueKey2 in valueSet:
                    if len(valueKey2) == 3:
                        continue
                    if valueKey2[0] == valueKey1[0] and valueKey2[1] == valueKey1[1] and len(valueDict[valueKey1]) == 1 and len(valueDict[valueKey2]) == 1: 
                        if operationList[0] in ["Branch", "Associate", "AncestorBranch", "AncestorAssociate"]:
                            valueDict[valueKey1] = [valueDict[valueKey1][0][:], valueDict[valueKey2][0][:]]
                        elif operationList[1] in ["Branch", "Associate", "AncestorBranch", "AncestorAssociate"]:
                            valueDict[valueKey1] = [valueDict[valueKey2][0][:], valueDict[valueKey1][0][:]] 
    return valueDict           

### Get locla knowledge for the current configuration, this is essential for preprocessing.
def getLocalKnowledge(outputDirName):
    resourceStringListView = json.load(open("../regoFiles/repoStringListView.json", "r"))
    resourceView = json.load(open("../regoFiles/repoView.json", "r"))
    resourceDependencyView = json.load(open("../regoFiles/repoDependencyView.json", "r"))
    planJsonData = json.load(open(f"{outputDirName}/plan.json", "r"))
    configJsonData = json.load(open(f"{outputDirName}/config.json", "r"))
    dependencyListJsonData = json.load(open(f"{outputDirName}/dependencyList.json", "r"))
    referencesPredDictJsonData = json.load(open(f"{outputDirName}/referencesPredDict.json", "r"))
    referencesSuccDictJsonData = json.load(open(f"{outputDirName}/referencesSuccDict.json", "r"))
    offspringDictJsonData = json.load(open(f"{outputDirName}/offspringDict.json", "r"))
    naiveAncestorDictJsonData = json.load(open(f"{outputDirName}/naiveAncestorDict.json", "r"))
    inclusiveAncestorDictJsonData = json.load(open(f"{outputDirName}/inclusiveAncestorDict.json", "r"))
    #artificialAncestorDictJsonData = json.load(open(f"{outputDirName}/artificialAncestorDict.json", "r"))
    plan = planJsonData["result"][0]["expressions"][0]["value"]
    config = configJsonData["result"][0]["expressions"][0]["value"]
    dependencyList = dependencyListJsonData["result"][0]["expressions"][0]["value"]
    referencesPredDict = referencesPredDictJsonData["result"][0]["expressions"][0]["value"]
    referencesSuccDict = referencesSuccDictJsonData["result"][0]["expressions"][0]["value"]
    offspringDict = offspringDictJsonData["result"][0]["expressions"][0]["value"]
    ancestorDict = naiveAncestorDictJsonData["result"][0]["expressions"][0]["value"]
    inclusiveAncestorDict = inclusiveAncestorDictJsonData["result"][0]["expressions"][0]["value"]
    #artificialAncestorDict = artificialAncestorDictJsonData["result"][0]["expressions"][0]["value"]
    return resourceStringListView, resourceView, resourceDependencyView, plan, config, dependencyList, referencesPredDict, referencesSuccDict, offspringDict, ancestorDict, inclusiveAncestorDict

### Main function for negative test case generation, calls up SMTMaster to instrument and evaluate SMT formula
### There could be two purposes: GEN which means negative test case generation, and "MDC" which means obtaining
### minimal deployable configuration. In practice, we firstly run MDC to get the minimzied configuration, then deploy 
### it as the positive validation step. We then run GEN to upon the MDC result to obtain a mutated configuration that
### serve as the nagative validation phase.
def rego2SMTConversion(outputDirName, mappingDirName, testRule, validatedRuleList, candidateRuleList, resourceType, optimization, purpose="GEN", iteration = 0, MDCResources=defaultdict(list), direction = True, resolve = True):
    start_time = time.time()
    resultDict = defaultdict(list)
    try:
        resourceStringListView, resourceView, resourceDependencyView, plan, config, dependencyList, referencesPredDict, \
            referencesSuccDict, offspringDict, ancestorDict, inclusiveAncestorDict = getLocalKnowledge(outputDirName)
        typeMappingPath = os.path.join(mappingDirName, "type.json")
        typeMapping = json.load(open(typeMappingPath, "r"))
        globalTypeMapping = json.load(open("../folderFiles/globalType.json", "r"))
        globalAncestorDict = json.load(open("../regoFiles/globalAncestorDict.json", "r"))
        globalSuccessorDict = json.load(open("../regoFiles/globalSuccessorDict.json", "r"))
    except Exception as e:
        print("Something went wrong when trying to capture local knowledge", e)
        return
    print("Debugging point after rego retrieval:", time.time()-start_time)
    print("Raw number of resources: ", len(plan))
    
    violationRow = testRule
    ruleList = validatedRuleList + candidateRuleList
    if violationRow not in ruleList:
        ruleList = [violationRow] + ruleList[:]
    print(f"Length of rule list: {len(ruleList)}")
    smtFormula = SMTMaster.SMTMaster()
    smtFormula.optimizer_init(optimization, purpose)
    
    originalDependencyList = dependencyList[:]
    plan, planFiltered, planOriginal, waivedSet, virtualResourceDict, new2oldMapping, additionalGraphTypeDict, \
        additionalResource, vNodeCount, relatedResourceTypes, dependencyList, removedEdges, originalDependencyList, ignoredResourceSet = \
        virtualResourceInit(resourceType, violationRow, plan, ancestorDict, inclusiveAncestorDict, \
        referencesPredDict, purpose, MDCResources, typeMapping, globalTypeMapping, dependencyList, \
        globalAncestorDict, globalSuccessorDict, resourceDependencyView, originalDependencyList)
    
    resultDict["plan"] = planFiltered
    resultDict["planOriginal"] = planOriginal
    resultDict["vNodeCount"] = vNodeCount
    resultDict["relatedResourceTypes"] = relatedResourceTypes
    resultDict["ignoredResourceSet"] = ignoredResourceSet
    
    targetViolationList = []
    if purpose == "MDC":
        if len(planFiltered) > 60 or len(planFiltered) < 2:
            print("MDC Configuration too small or large to handle even after preprocessing, try another one?")
            return
    else:
        if len(planFiltered) > 80 or len(planFiltered) < 2:
            print("GEN Configuration too small or large to handle even after preprocessing, try another one?")
            return
    ### This needs to be called first because it is literally the infrastructure for topo-related SMT encoding
    if purpose == "AGGATTR":
        for newEdge in MDCResources["dependency"][:]:
            newNode1 = ".".join(newEdge[1].split(".")[:2])
            newNode2 = ".".join(newEdge[0].split(".")[:2])
            newPort1 = ".".join(newEdge[1].split(".")[2:])
            newPort2 = ".".join(newEdge[0].split(".")[2:])
            dependencyList.append([newNode1, newNode2, newPort1, newPort2, "", ""])
            for index in range(1, int(MDCResources["vNodeCount"])):
                if "ZODIAC-" in newNode1 and "ZODIAC-" in newNode2:
                    intNode1 = newNode1[:-2] + "-" + str(index)
                    intNode2 = newNode2[:-2] + "-" + str(index)
                    dependencyList.append([intNode1, intNode2, newPort1, newPort2, "", ""])
                    MDCResources["dependency"].append([intNode2+"."+newPort2, intNode1+"."+newPort1])
                elif "ZODIAC-" in newNode1:
                    intNode1 = newNode1[:-2] + "-" + str(index)
                    dependencyList.append([intNode1, newNode2, newPort1, newPort2, "", ""])
                    MDCResources["dependency"].append([newNode2+"."+newPort2, intNode1+"."+newPort1])
                elif "ZODIAC-" in newNode2:
                    intNode2 = newNode2[:-2] + "-" + str(index)
                    dependencyList.append([newNode1, intNode2, newPort1, newPort2, "", ""])
                    MDCResources["dependency"].append([intNode2+"."+newPort2, newNode1+"."+newPort1])
    print("dependencyList:", dependencyList)
    smtFormula.generate_reference_infra(dependencyList, originalDependencyList, planFiltered, plan, resourceDependencyView, virtualResourceDict, waivedSet, purpose, additionalGraphTypeDict)
    print("Debugging point after generating topology smt infrastructure:", time.time()-start_time)
    
    smtFormula.valueStringDict = resourceStringListView
    smtFormula.valueConstantDict = resourceView
    startIndex = 1
    flagMatched = False
    violationDetailDict = defaultdict(list)
    conflictResolver = defaultdict()
    for row in ruleList:
        if purpose == "MDC" and row != violationRow:
            continue
        elif purpose == "AGGTOPO" and row != violationRow:
            
            if "ReferenceThen" in row[1] or "NegationThen" in row[1]:
                if row[2].split(".")[0] == row[3].split(".")[0]:
                    continue
            elif "ThenReference" in row[1] or "ThenNegation" in row[1]:
                if row[-2].split(".")[0] == row[-1].split(".")[0]:
                    continue
        elif purpose == "AGGATTR" and row != violationRow:
            if row[0] in ["TOPO"]:
                continue
            if "ReferenceThen" in row[1] or "NegationThen" in row[1]:
                if row[2].split(".")[0] == row[3].split(".")[0]:
                    continue
            elif "ThenReference" in row[1] or "ThenNegation" in row[1]:
                if row[-2].split(".")[0] == row[-1].split(".")[0]:
                    continue
        if purpose in ["AGGATTR", "AGGTOPO"] and row != violationRow:
            countItem = 0
            countRelated = 0
            
            completeResourceTypeSet = set()
            for resourceBlock in planFiltered:
                completeResourceTypeSet.add(resourceBlock["type"])
            for rowItem in row[2:]:
                countItem += 1
                for relatedType in completeResourceTypeSet:
                    if relatedType == rowItem.split(".")[0]:
                        countRelated += 1
                        break
            if countItem > countRelated:
                continue
        operationList = row[1].split("If")
        operationList = operationList[0].split("Then")
        if len(operationList) != 2:
            continue
        valueDict = getValueDict(operationList, row, planFiltered, config, conflictResolver, purpose)
        if valueDict == None:
            continue
        
        for valueKey in valueDict:
            if len(valueDict[valueKey]) != 2:
                continue 
            valueArray1 = valueDict[valueKey][0][:]
            valueArray1.append("Condition")
            valueArray2 = valueDict[valueKey][1][:]
            valueArray2.append("Statement")
            valueArrayList =[valueArray1, valueArray2]
            flagEssence = False
            if row == violationRow and flagMatched == False and (purpose == "GEN" or purpose == "AGGTOPO"):
                flagEssence = True
            for valueIndex, valueArray in enumerate(valueArrayList):
                
                if operationList[valueIndex] in ["Absence", "Existence", "Constant", "AbsenceComboUp", "ExistenceComboUp", \
                                                 "AbsenceComboDown", "ExistenceComboDown", "ConstantComboUp", "ConstantComboDown", \
                                                 "NonConstant", "NonConstantComboDown", "NonConstantComboUp"]:
                    smtFormula.generate_enum_mutation([valueArray], startIndex, optimization)
                elif operationList[valueIndex] in ["Equal", "Unequal", "EqualCombo", "UnequalCombo"]:
                    if purpose == "AGGATTR":
                        smtFormula.generate_equality_mutation([valueArray], startIndex, optimization, int(MDCResources["vNodeCount"]))
                    else:
                        smtFormula.generate_equality_mutation([valueArray], startIndex, optimization, vNodeCount)
                elif operationList[valueIndex] in ["BinConstantCombo"]:
                    smtFormula.generate_bin_enum_mutation([valueArray], startIndex, optimization)
                elif operationList[valueIndex] in ["CIDRInclude", "CIDRExclude", "CIDRIncludeCombo", "CIDRExcludeCombo"]:
                    smtFormula.generate_CIDR_mutation([valueArray], startIndex, optimization)
                elif operationList[valueIndex] in ["Reference", "Exclusive", "ConflictChild", "Negation", "AncestorReference", "AncestorConflictChild", "AggParent", "AggChild"]:
                    smtFormula.generate_topology_binary_mutation([valueArray], startIndex, flagEssence)
                elif operationList[valueIndex] in ["Branch", "Associate", "Intra", "AncestorBranch", "AncestorAssociate"]:
                    smtFormula.generate_topology_ternary_mutation([valueArray], startIndex, flagEssence)
                elif operationList[valueIndex] in ["CIDRRange"]:
                    smtFormula.generate_mask_mutation([valueArray], startIndex, optimization)
            violationCount_index = z3.Int(f"violationCount_{startIndex}")
            
            if row in candidateRuleList or row == violationRow:
                if row[0] == "TOPO":
                    smtFormula.violationCount_TOPO_list.append(violationCount_index)
                smtFormula.violationCount_list.append(violationCount_index)
            elif row in validatedRuleList:
                smtFormula.violationCount_VAL_list.append(violationCount_index)
                
            smtFormula.countDict[f"violationCount_{startIndex}"] = violationCount_index
            conditionCount_index = smtFormula.countDict[f"conditionCount_{startIndex}"]
            statementCount_index = smtFormula.countDict[f"statementCount_{startIndex}"]
            violationDetailDict[f"violationCount_{startIndex}"] = [valueArrayList, tuple(row)]
            if row == violationRow:
                print("Match: ", startIndex, violationRow, valueDict[valueKey])
                ### We want to enfoce one and only one rule violation instance.
                
                flagMatched = True
                if purpose == "GEN" or purpose == "AGGTOPO" or purpose == "AGGATTR":
                    targetViolationList.append(violationCount_index)
                
            if purpose == "GEN" or purpose == "AGGTOPO" or purpose == "AGGATTR":
                ### define what violation means (if cond then not stat) for negative test case generation
                smtFormula.optimizer.add(violationCount_index == z3.If(z3.Not(z3.Or([conditionCount_index == 0, statementCount_index == 1])), 1, 0))
            elif purpose == "MDC":
                ### define what violation means (cond and stat for target rule) for minimal deployable configuration generation
                if operationList[0] in ["AggParent", "AggChild", "NonConstant", "CIDRRange"] or \
                   operationList[1] in ["AggParent", "AggChild", "NonConstant", "CIDRRange"]:
                    smtFormula.optimizer.add(violationCount_index == (statementCount_index == 1))
                else:
                    smtFormula.optimizer.add(violationCount_index == z3.And(conditionCount_index == 1, statementCount_index == 1))
                ### we strongly prefer results where target rule instances are in conformance (do we really need this given no changes are possible?)
                smtFormula.optimizer.add_soft(violationCount_index == 1)
            
            startIndex += 1
    ### changes made for target rule mutation logic
    if purpose == "GEN" or purpose == "AGGTOPO" or purpose == "AGGATTR":
        smtFormula.optimizer.add(z3.Sum(targetViolationList) >= 1)
    
    print("conflictResolver", conflictResolver, flagMatched)        
    if flagMatched == False:
        return resultDict
    print("Debugging point after smt formula generation: ", time.time()-start_time)
    print("Size of formula: ", len(smtFormula.optimizer.assertions()))
    ruleType = violationRow[0]
    sumDict = smtFormula.optimizer_summarize(optimization, purpose, ruleType, direction, iteration, resolve)
    
    check_result = smtFormula.optimizer_check()
    print("Satisfiability: ", check_result)
    if str(check_result) == "unsat":
        resultDict["satisfiability"] = False
        return resultDict
    resultDict["satisfiability"] = True
    modelPerIndex = smtFormula.optimizer_model()
    
    print("Debugging point after smt solving: ", time.time()-start_time)
    if purpose == "GEN" or purpose == "AGGTOPO" or purpose == "AGGATTR":
        resultDict = analyzeSMTGENResult(modelPerIndex, smtFormula, violationDetailDict, planFiltered, resourceDependencyView, testRule, violationRow, sumDict, resultDict, new2oldMapping, additionalResource, purpose, MDCResources)
    elif purpose == "MDC":
        if len(planFiltered)+len(planOriginal) > 20:
            return None
        resultDict = analyzeSMTMDCResult(modelPerIndex, violationDetailDict, resultDict, violationRow, globalSuccessorDict, resourceDependencyView, planFiltered)
        resultDict["ancestorDict"] = ancestorDict
        resultDict["inclusiveAncestorDict"] = inclusiveAncestorDict
        resultDict["referencesSuccDict"] = referencesSuccDict
    print("Debugging point at the end of the smt solving pipeline:", time.time()-start_time)
    
    return resultDict
