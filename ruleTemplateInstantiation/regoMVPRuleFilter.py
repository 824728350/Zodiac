import os
import sys
sys.path.insert(0, '..')
import utils.utils as utils
import csv
from collections import defaultdict
import argparse
from utils.utils import *
import json
import knowledgeBaseConstruction.regoMVPGetKnowledgeBase as regoMVPGetKnowledgeBase
import ipaddress
import multiprocessing
import regoMVPRulePlainText
import regoMVPRuleInterpolate

def positiveValidation(operation, opType, row, rowIndex, planRaw, config, dependencyList, referencesPredDict, referencesSuccDict, offspringDict, naiveAncestorDict, valueDict, topoDict, operationList, repoImportance, schemaDetailView):
    plan = []
    flagDiscard = False
    for resourceBlock in planRaw:
        if "data." != resourceBlock["address"][:5]:
            plan.append(resourceBlock)
    if operation in ["Absence", "Existence", "Constant", "AbsenceComboUp", "ExistenceComboUp", "AbsenceComboDown", "ExistenceComboDown", \
                     "ConstantComboUp", "ConstantComboDown"]:
        resourceType = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceAttr = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
        resourceValue = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        rowIndex += 1
    
        for resourceBlock in plan:
            if resourceBlock["type"] == resourceType:
                resourceName = resourceBlock["address"]
                try:
                    if "." not in resourceAttr:
                        attributeValue = resourceBlock["values"][resourceAttr]
                    else:
                        resourceAttrList = resourceAttr.split(".")
                        if len(resourceAttrList) > 2:
                            return rowIndex, valueDict, True
                        else:
                            attributeValue = resourceBlock["values"][resourceAttrList[0]][0][resourceAttrList[1]]
                except:
                    return rowIndex, valueDict, True
                if operation in ["Absence", "Existence", "AbsenceComboUp", "ExistenceComboUp", "AbsenceComboDown", "ExistenceComboDown"]:
                    if attributeValue == None or attributeValue == [] or attributeValue == {}:
                        attributeValue = "Absence"
                    else:
                        attributeValue = "Existence"
                    #
                    if operation in ["Absence", "Existence"]:
                        valueDict[(resourceName,resourceName)].append(attributeValue == resourceValue)
                    elif operation in ["AbsenceComboUp", "ExistenceComboUp"]:
                        for resourceBlock2 in plan:
                            resourceName2 = resourceBlock2["address"]
                            valueDict[(resourceName2, resourceName)].append(attributeValue == resourceValue)
                    elif operation in ["AbsenceComboDown", "ExistenceComboDown"]:
                        for resourceBlock2 in plan:
                            resourceName2 = resourceBlock2["address"]
                            valueDict[(resourceName, resourceName2)].append(attributeValue == resourceValue)
                elif operation in ["Constant", "ConstantComboUp", "ConstantComboDown"]:
                    if attributeValue == True:
                        attributeValue = "true"
                    elif attributeValue == False:
                        attributeValue = "false"
                    if operation in ["Constant"]:
                        valueDict[(resourceName,resourceName)].append(attributeValue == resourceValue)
                    elif operation in ["ConstantComboUp"]:
                        for resourceBlock2 in plan:
                            resourceName2 = resourceBlock2["address"]
                            valueDict[(resourceName2, resourceName)].append(attributeValue == resourceValue)
                    elif operation in ["ConstantComboDown"]:
                        for resourceBlock2 in plan:
                            resourceName2 = resourceBlock2["address"]
                            valueDict[(resourceName, resourceName2)].append(attributeValue == resourceValue)
                    
    elif operation in ["Equal", "Unequal", "CIDRInclude", "CIDRExclude", "EqualCombo", "UnequalCombo", "CIDRIncludeCombo", "CIDRExcludeCombo", "BinConstantCombo"]:
        resourceType1 = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceAttr1 = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
        resourceValue1 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resourceType2 = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        resourceAttr2 = row[rowIndex+1][find_nth(row[rowIndex+1], ".", 1)+1:find_nth(row[rowIndex+1], "=", 1)-1]
        resourceValue2 = row[rowIndex+1][find_nth(row[rowIndex+1], "=", 2)+2:]
        for index1, resourceBlock1 in enumerate(plan):
            for index2, resourceBlock2 in enumerate(plan):
                if resourceBlock1["type"] != resourceType1 or resourceBlock2["type"] != resourceType2:
                    continue
                elif "ATTR" in opType and index1 != index2:
                    continue
                elif "COMBO" in opType and index1 == index2:
                    continue
                resourceName1 = resourceBlock1["address"]
                resourceName2 = resourceBlock2["address"]
                try:
                    if "." not in resourceAttr1:
                        attributeValue1 = resourceBlock1["values"][resourceAttr1]
                    else:
                        resourceAttrList1 = resourceAttr1.split(".")
                        if len(resourceAttrList1) > 2:
                            return rowIndex, valueDict, True
                        else:
                            attributeValue1 = resourceBlock1["values"][resourceAttrList1[0]][0][resourceAttrList1[1]]
                    if "." not in resourceAttr2:
                        attributeValue2 = resourceBlock2["values"][resourceAttr2]
                    else:
                        resourceAttrList2 = resourceAttr2.split(".")
                        if len(resourceAttrList2) > 2:
                            return rowIndex, valueDict, True
                        else:
                            if "ATTR" in opType:
                                attributeValue2 = resourceBlock2["values"][resourceAttrList2[0]][1][resourceAttrList2[1]]
                            elif "COMBO" in opType:
                                attributeValue2 = resourceBlock2["values"][resourceAttrList2[0]][0][resourceAttrList2[1]]
                except:
                    return rowIndex, valueDict, True
                if type(attributeValue1) == list and len(attributeValue1) >= 1:
                    attributeValue1 = attributeValue1[0]
                if type(attributeValue2) == list and len(attributeValue2) >= 1:
                    attributeValue2 = attributeValue2[0]
                if operation in ["Equal", "EqualCombo"]:
                    valueDict[(resourceName1, resourceName2)].append(attributeValue1 == attributeValue2)
                elif operation in ["Unequal", "UnequalCombo"]:
                    valueDict[(resourceName1, resourceName2)].append(attributeValue1 != attributeValue2)     
                elif operation in ["CIDRExclude", "CIDRExcludeCombo"]:
                    try:
                        #print("CIDRExclude", attributeValue1, attributeValue2)
                        cidr1 = ipaddress.ip_network(attributeValue1)
                        cidr2 = ipaddress.ip_network(attributeValue2)
                        valueDict[(resourceName1, resourceName2)].append(not cidr1.overlaps(cidr2))
                    except:
                        continue
                elif operation in ["CIDRInclude", "CIDRIncludeCombo"]:
                    try:
                        #print("CIDRInclude", attributeValue1, attributeValue2)
                        cidr1 = ipaddress.ip_network(attributeValue1)
                        cidr2 = ipaddress.ip_network(attributeValue2)
                        valueDict[(resourceName1, resourceName2)].append(cidr1.subnet_of(cidr2))
                    except:
                        continue
                elif operation in ["BinConstantCombo"]:
                    if attributeValue1 == True:
                        attributeValue1 = "true"
                    elif attributeValue1 == False:
                        attributeValue1 = "false"
                    if attributeValue2 == True:
                        attributeValue2 = "true"
                    elif attributeValue2 == False:
                        attributeValue2 = "false"
                    valueDict[(resourceName1, resourceName2)].append(not(attributeValue1 == resourceValue1) or attributeValue2 == resourceValue2)
        rowIndex += 2
    elif operation in ["Reference", "AncestorReference"]:
        resourceType1 = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceAttr1 = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
        resourceValue1 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resourceType2 = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        resourceAttr2 = row[rowIndex+1][find_nth(row[rowIndex+1], ".", 1)+1:find_nth(row[rowIndex+1], "=", 1)-1]
        resourceValue2 = row[rowIndex+1][find_nth(row[rowIndex+1], "=", 2)+2:]
        flagValidDict = defaultdict()
        flattendAttrList = []
        for ele in resourceAttr1.split("."):
            if ele.isnumeric() and ele not in ["0", "1"]:
                flagDiscard = True
            elif operationList[0] not in ["Intra"] and operationList[1] not in ["Intra"]:
                if ele.isnumeric() and ele != "0":
                    flagDiscard = True
        
        if operation in ["Reference"]:
            if rowIndex != 2:
                if len(resourceAttr1.split(".")) == 1:
                    if resourceType1 in schemaDetailView and resourceAttr1 in schemaDetailView[resourceType1]:
                        if schemaDetailView[resourceType1][resourceAttr1] == "required":
                            flagDiscard = True
                elif len(resourceAttr1.split(".")) == 3:
                    cleansedResourceAttr1 = resourceAttr1.split(".")[0] + "." + resourceAttr1.split(".")[-1]
                    if resourceType1 in schemaDetailView and cleansedResourceAttr1 in schemaDetailView[resourceType1]:
                        if schemaDetailView[resourceType1][cleansedResourceAttr1] == "required":
                            flagDiscard = True
            for name1, name2, attr1, attr2, _, _ in dependencyList:
                type1 = name1.split(".")[0]
                type2 = name2.split(".")[0]
                if type1 == resourceType1 and type2 == resourceType2:
                    if attr1 == resourceAttr1 and attr2 == resourceAttr2:
                        flagValidDict[(name1, name2)] = True
        else:
            for name1 in naiveAncestorDict:
                for name2 in naiveAncestorDict[name1]:
                    type1 = name1.split(".")[0]
                    type2 = name2.split(".")[0]
                    if type1 == resourceType1 and type2 == resourceType2:
                        flagValidDict[(name1, name2)] = True
        
        reservedSetChild = set()
        reservedSetParent = set()
        for key in flagValidDict:
            valueDict[key].append(flagValidDict[key])
            name1, name2 = key[0], key[1]
            reservedSetChild.add(name1)
            reservedSetParent.add(name2)
            topoDict[key].append(flagValidDict[key])
        
        for _, resourceBlock in enumerate(plan):
            resourceName = resourceBlock["address"]
            resourceTypeName = resourceBlock["type"]
            if resourceTypeName == resourceType1:
                if resourceName not in reservedSetChild:
                    if "[" not in resourceName and "module." not in resourceName:
                        valueDict[(resourceName, resourceName)].append(False)
            if resourceTypeName == resourceType2:
                if resourceName not in reservedSetParent:
                    if "[" not in resourceName and "module." not in resourceName:
                        valueDict[(resourceName, resourceName)].append(False)
        rowIndex += 2
    elif operation in ["Negation"]:
        resourceType1 = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceAttr1 = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
        resourceValue1 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resourceType2 = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        resourceAttr2 = row[rowIndex+1][find_nth(row[rowIndex+1], ".", 1)+1:find_nth(row[rowIndex+1], "=", 1)-1]
        resourceValue2 = row[rowIndex+1][find_nth(row[rowIndex+1], "=", 2)+2:]
        flagValidDict = defaultdict()
        for ele in resourceAttr1.split("."):
            if ele.isnumeric() and ele != "0":
                flagDiscard = True
                
        for index1, resourceBlock1 in enumerate(plan):
            resourceName1 = resourceBlock1["address"]
            resourceTypeName1 = resourceBlock1["type"]
            if resourceTypeName1 == resourceType1: 
                flagConflict = False
                for name1, name2, attr1, attr2, _, _ in dependencyList:
                    type1 = name1.split(".")[0]
                    type2 = name2.split(".")[0]
                    if name1 == resourceName1 and attr1 == resourceAttr1:
                        #print("negation detected!")
                        flagConflict = True
                if flagConflict == False:
                    flagValidDict[(resourceName1, resourceName1)] = True
                else:
                    flagValidDict[(resourceName1, resourceName1)] = False
            
        for key in flagValidDict:
            valueDict[key].append(flagValidDict[key])
            topoDict[key].append(flagValidDict[key])
        rowIndex += 2
    elif operation in ["Branch", "AncestorBranch"]:
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
        flagValidDict = defaultdict()
        flagInvalidDict = defaultdict()
        normalSet = set()
        for ele in resourceAttr1.split("."):
            if ele.isnumeric() and ele != "0":
                flagDiscard = True
        for ele in resourceAttr2.split("."):
            if ele.isnumeric() and ele != "0":
                flagDiscard = True
        if operation in ["Branch"]:
            for name1, name3, attr1, attr3, _, _ in dependencyList:
                type1 = name1.split(".")[0]
                type3 = name3.split(".")[0]
                if (type1 == resourceType1 and type3 == resourceType3) or (type1 == resourceType2 and type3 == resourceType4):
                    normalSet.add(name1)
                    normalSet.add(name3)
                for name2, name4, attr2, attr4, _, _ in dependencyList:
                    type2 = name2.split(".")[0]
                    type4 = name4.split(".")[0]    
                    if name3 == name4 and name1 != name2 and type1 == resourceType1 and type2 == resourceType2 and type3 == resourceType3 and type4 == resourceType4:
                        if attr1 == resourceAttr1 and attr2 == resourceAttr2 and attr3 == resourceAttr3 and attr4 == resourceAttr4:
                            flagValidDict[(name1, name2)] = True
                    elif type1 == resourceType1 and type2 == resourceType2 and type3 == resourceType3 and type4 == resourceType4:
                        flagInvalidDict[(name1, name2)] = False
        else:
            for name1 in naiveAncestorDict:
                for name3 in naiveAncestorDict[name1]:
                    type1 = name1.split(".")[0]
                    type3 = name3.split(".")[0]
                    if (type1 == resourceType1 and type3 == resourceType3) or (type1 == resourceType2 and type3 == resourceType4):
                        normalSet.add(name1)
                        normalSet.add(name3)
                    for name2 in naiveAncestorDict:
                        for name4 in naiveAncestorDict[name2]:
                            type2 = name2.split(".")[0]
                            type4 = name4.split(".")[0]  
                            if name3 == name4 and name1 != name2 and type1 == resourceType1 and type2 == resourceType2 and type3 == resourceType3 and type4 == resourceType4:
                                flagValidDict[(name1, name2)] = True
                            elif type1 == resourceType1 and type2 == resourceType2 and type3 == resourceType3 and type4 == resourceType4:
                                flagInvalidDict[(name1, name2)] = False   
                        
       
        for key in flagValidDict:
            valueDict[key].append(flagValidDict[key])
            topoDict[key].append(flagValidDict[key])
        for key in flagInvalidDict:
            if key not in flagValidDict:
                valueDict[key].append(flagInvalidDict[key])
        rowIndex += 4
    elif operation in ["Associate", "AncestorAssociate"]:
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
        flagValidDict = defaultdict()
        flagInvalidDict = defaultdict()
        normalSet = set()
        
        for ele in resourceAttr1.split("."):
            if ele.isnumeric() and ele != "0":
                flagDiscard = True
        for ele in resourceAttr2.split("."):
            if ele.isnumeric() and ele not in ["0"]:
                flagDiscard = True
            
        if operation in ["Associate"]:
            for name1, name3, attr1, attr3, _, _ in dependencyList:
                type1 = name1.split(".")[0]
                type3 = name3.split(".")[0]
                if (type1 == resourceType1 and type3 == resourceType3) or (type1 == resourceType2 and type3 == resourceType4):
                    normalSet.add(name1)
                    normalSet.add(name3)
                if rowIndex != 2 and resourceType3 == resourceType4 and attr1 == resourceAttr1 and attr3 == resourceAttr3:
                    flagValidDict[(name1, name3)] = True
                    continue
                for name2, name4, attr2, attr4, _, _ in dependencyList:
                    type2 = name2.split(".")[0]
                    type4 = name4.split(".")[0]
                    
                    if name1 == name2 and name3 != name4 and type1 == resourceType1 and type2 == resourceType2 and type3 == resourceType3 and type4 == resourceType4:   
                        if attr1 == resourceAttr1 and attr2 == resourceAttr2 and attr3 == resourceAttr3 and attr4 == resourceAttr4:
                            if operationList[0] in ["Reference"] or operationList[1] in ["Reference"]:
                                flagValidDict[(name1, name3)] = True
                            else:
                                flagValidDict[(name3, name4)] = True
                    elif type1 == resourceType1 and type2 == resourceType2 and type3 == resourceType3 and type4 == resourceType4:
                        flagInvalidDict[(name3, name4)] = False
        else:
            for name1 in naiveAncestorDict:
                for name3 in naiveAncestorDict[name1]:
                    type1 = name1.split(".")[0]
                    type3 = name3.split(".")[0]
                    if (type1 == resourceType1 and type3 == resourceType3) or (type1 == resourceType2 and type3 == resourceType4):
                        normalSet.add(name1)
                        normalSet.add(name3)
                    for name2 in naiveAncestorDict:
                        for name4 in naiveAncestorDict[name2]:
                            type2 = name2.split(".")[0]
                            type4 = name4.split(".")[0]
                            if name1 == name2 and name3 != name4  and type1 == resourceType1 and type2 == resourceType2 and type3 == resourceType3 and type4 == resourceType4: 
                                if operationList[0] in ["AncestorReference"] or operationList[1] in ["AncestorReference"]:
                                    flagValidDict[(name1, name3)] = True
                                else:
                                    flagValidDict[(name3, name4)] = True
                            elif type1 == resourceType1 and type2 == resourceType2 and type3 == resourceType3 and type4 == resourceType4:
                                flagInvalidDict[(name3, name4)] = False
                            
        for key in flagValidDict:
            valueDict[key].append(flagValidDict[key])
            topoDict[key].append(flagValidDict[key])
        for key in flagInvalidDict:
            if key not in flagValidDict:
                valueDict[key].append(flagInvalidDict[key])
        rowIndex += 4
    elif operation in ["Exclusive"]:
        resourceType1 = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceAttr1 = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
        resourceValue1 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resourceType2 = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        resourceAttr2 = row[rowIndex+1][find_nth(row[rowIndex+1], ".", 1)+1:find_nth(row[rowIndex+1], "=", 1)-1]
        resourceValue2 = row[rowIndex+1][find_nth(row[rowIndex+1], "=", 2)+2:]
        flagValidDict = defaultdict()
        flagInvalidDict = defaultdict()
        for ele in resourceAttr1.split("."):
            if ele.isnumeric() and ele != "0":
                flagDiscard = True
        for name1, name2, attr1, attr2, _, _ in dependencyList:
            type1 = name1.split(".")[0]
            type2 = name2.split(".")[0]
            if type1 == resourceType1 and type2 == resourceType2 and len(referencesSuccDict[name2]) == 1:
                #print("exclusiveness detected!")
                flagValidDict[(name1, name2)] = True
            else:
                flagInvalidDict[(name1, name2)] = False
            
        for key in flagValidDict:
            valueDict[key].append(flagValidDict[key])
            topoDict[key].append(flagValidDict[key])
        for key in flagInvalidDict:
            if key not in flagValidDict:
                valueDict[key].append(flagInvalidDict[key])
        rowIndex += 2
    elif operation in ["ConflictChild", "AncestorConflictChild"]:
        resourceType1 = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceAttr1 = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
        resourceValue1 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resourceType2 = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        resourceAttr2 = row[rowIndex+1][find_nth(row[rowIndex+1], ".", 1)+1:find_nth(row[rowIndex+1], "=", 1)-1]
        resourceValue2 = row[rowIndex+1][find_nth(row[rowIndex+1], "=", 2)+2:]
        flagValidDict = defaultdict()
        flagInvalidDict = defaultdict()
        for ele in resourceAttr1.split("."):
            if ele.isnumeric() and ele != "0":
                flagDiscard = True
        if operation in ["ConflictChild"]:
            for name1, name2, attr1, attr2, _, _ in dependencyList:
                type1 = name1.split(".")[0]
                type2 = name2.split(".")[0]
                if type1 == resourceType1 and type2 == resourceType2:
                    flagConflict = False
                    
                    for ele in referencesSuccDict[name2]:
                        if ele.split(".")[0] == resourceType1 and ele != name1:
                            flagConflict = True
                            flagInvalidDict[(name1, name2)] = False
                            break
                    if flagConflict == False:
                        #print("no conflictchild detected!")
                        flagValidDict[(name1, name2)] = True
                    
        else:
            for name1 in naiveAncestorDict:
                for name2 in naiveAncestorDict[name1]:
                    type1 = name1.split(".")[0]
                    type2 = name2.split(".")[0]
                    if type1 == resourceType1 and type2 == resourceType2:
                        flagConflict = False
                        
                        for ele in offspringDict[name2]:
                            if ele.split(".")[0] == resourceType1 and ele != name1:
                                flagConflict = True
                                flagInvalidDict[(name1, name2)] = False
                                break
                        if flagConflict == False:
                            #print("conflictchild detected!")
                            flagValidDict[(name1, name2)] = True
                            
        for key in flagValidDict:
            valueDict[key].append(flagValidDict[key])
            topoDict[key].append(flagValidDict[key])
        for key in flagInvalidDict:
            if key not in flagValidDict:
                valueDict[key].append(flagInvalidDict[key])
        rowIndex += 2
    elif operation in ["Intra"]:
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
        flagValidDict = defaultdict()
        flagInvalidDict = defaultdict()
        normalSet = set()
        for ele in resourceAttr1.split("."):
            if ele.isnumeric() and ele != "0":
                flagDiscard = True
        for ele in resourceAttr2.split("."):
            if ele.isnumeric() and ele != "1":
                flagDiscard = True
        for name1, name3, attr1, attr3, _, _ in dependencyList:
            for name2, name4, attr2, attr4, _, _ in dependencyList:
                type1 = name1.split(".")[0]
                type2 = name2.split(".")[0]
                type3 = name3.split(".")[0]
                type4 = name4.split(".")[0]
                if name1 == name2 and name3 == name4 and type1 == resourceType1 and type2 == resourceType2 and type3 == resourceType3 \
                   and type4 == resourceType4 and attr1 == resourceAttr1 and attr2 == resourceAttr2 and attr3 == resourceAttr3 and attr4 == resourceAttr4:
                    flagValidDict[(name1, name3)] = True
                elif type1 == resourceType1 and type2 == resourceType2 and type3 == resourceType3 and type4 == resourceType4:
                    flagInvalidDict[(name1, name3)] = False
        for key in flagValidDict:
            valueDict[key].append(flagValidDict[key])
            topoDict[key].append(flagValidDict[key])
        for key in flagInvalidDict:
            if key not in flagValidDict:
                valueDict[key].append(flagInvalidDict[key])
        rowIndex += 4
    
    return rowIndex, valueDict, flagDiscard

def filterInBatch(resourceType, operatorAndDirection, csvFileName, csvFilteredFileName, regoFolderName, poolSize=16):
    utils.execute_cmd_imm(f"rm -rf ../filterRuleExpressionInput/*")
    utils.execute_cmd_imm(f"rm -rf ../filterRuleExpressionOutput/*")
    arglists = []
    
    csvFile = open(csvFileName, "r")
    csvReader = csv.reader(csvFile, delimiter=',')
    jsonRuleData = []
    for row in csvReader:
        if row[0] == "Operator":
            continue
        jsonRuleData.append(row)
    jsonFileName = csvFileName[:-4] + ".json"
    with open(jsonFileName, 'w') as f:
        json.dump(jsonRuleData, f, sort_keys = True, indent = 4)
    tempIndex = 0    
    for filename in os.listdir(regoFolderName):
        tempIndex += 1
        
        if ".rego" not in filename:
            continue
        filepath = os.path.join(regoFolderName, filename)
        identifier = filename[:-5]
        inputDirName = f"../filterRuleExpressionInput/{identifier}"
        outputDirName = f"../folderFiles/folders_{resourceType}_knowledge/{identifier}"
        os.mkdir(f"{inputDirName}")
        utils.execute_cmd_imm(f"cp {filepath} {inputDirName}/handled.rego")
        
        jsonFilteredName = f"{outputDirName}/filtered_{operatorAndDirection}.json"
        utils.execute_cmd_imm(f"rm -rf {outputDirName}/filtered_{operatorAndDirection}.json")
        arglists.append([jsonFileName, jsonFilteredName, inputDirName, outputDirName])
    
    pool = multiprocessing.Pool(processes=poolSize)
    for arglist in arglists:
        pool.apply_async(filterRuleExpression, args=arglist)
    pool.close()
    pool.join()
    
    candidateRules = set()
    ruleConfidencePositive = defaultdict(int)
    ruleConfidenceNegative = defaultdict(int)
    ruleAttrFlag = defaultdict()
    ruleConditionPositive = defaultdict(int)
    ruleConditionNegative = defaultdict(int)
    ruleStatementPositive = defaultdict(int)
    ruleStatementNegative = defaultdict(int)
    ruleJointPositive = defaultdict(int)
    ruleJointNegative = defaultdict(int)
    
    index = 0
    csvFilteredFile = open(csvFilteredFileName, "w")
    fields = ['Operator', 'Shape', 'Operand1', 'Operand2', 'Operand3', 'Operand4', 'Operand5', 'Operand6', 'Operand7', 'Operand8']
    csvWriter = csv.writer(csvFilteredFile)
    csvWriter.writerow(fields)
    resultDict = defaultdict()
    for filename in os.listdir(regoFolderName):
        if ".rego" not in filename:
            continue
        identifier = filename[:-5]
        outputDirName = f"../folderFiles/folders_{resourceType}_knowledge/{identifier}"
        jsonFilteredName = f"{outputDirName}/filtered_{operatorAndDirection}.json"
        
        try:
            jsonRuleData = json.load(open(f"{jsonFilteredName}", "r"))
        except Exception as e:
            print("Something went wrong when retrieving filtered rule files", e)
            continue
        if len(jsonRuleData) != 0:
            index += 1

        for rule in jsonRuleData:
            candidateRules.add(rule)
            if jsonRuleData[rule][0] == True:
                ruleConfidencePositive[rule] += 1
            else:
                ruleConfidenceNegative[rule] += 1
            ruleConditionPositive[rule] += jsonRuleData[rule][1]
            ruleConditionNegative[rule] += jsonRuleData[rule][2]
            ruleStatementPositive[rule] += jsonRuleData[rule][3]
            ruleStatementNegative[rule] += jsonRuleData[rule][4]
            ruleJointPositive[rule] += jsonRuleData[rule][5]
            ruleJointNegative[rule] += jsonRuleData[rule][6]
            ruleAttrFlag[rule] = jsonRuleData[rule][7]
    countConfidence = 0
    countLift = 0
    countLeft = 0
    for rule in candidateRules:

        print(rule, ruleConfidencePositive[rule], ruleConfidenceNegative[rule], index)
        flagTOPOCase = (rule.split("####")[0] != "TOPO" or ruleConfidencePositive[rule] == 0 or float(ruleConfidenceNegative[rule])/ruleConfidencePositive[rule] > 0.1)
        if index > 100:
            if ruleConfidenceNegative[rule] > 4 and flagTOPOCase:
                countConfidence += 1
                resultDict[rule] = "Confidence"
                continue
        elif index > 50:
            if ruleConfidenceNegative[rule] > 3 and flagTOPOCase:
                countConfidence += 1
                resultDict[rule] = "Confidence"
                continue
        elif index > 25:
            if ruleConfidenceNegative[rule] > 2 and flagTOPOCase:
                countConfidence += 1
                resultDict[rule] = "Confidence"
                continue
        else:
            if ruleConfidenceNegative[rule] > 1 and flagTOPOCase:
                countConfidence += 1
                resultDict[rule] = "Confidence"
                continue
        
        if ruleAttrFlag[rule] == True:
            try:
                print(ruleConditionPositive[rule], ruleConditionNegative[rule], ruleStatementPositive[rule], ruleStatementNegative[rule])
                conditionProb = float(ruleConditionPositive[rule])/(ruleConditionPositive[rule] + ruleConditionNegative[rule])
                statementProb = float(ruleStatementPositive[rule])/(ruleStatementPositive[rule] + ruleStatementNegative[rule])
                jointProb = float(ruleJointPositive[rule])/(ruleJointPositive[rule] + ruleJointNegative[rule])
                liftValue = jointProb/(conditionProb * statementProb)
                print(conditionProb, statementProb, jointProb, liftValue)
                if rule.split("####")[0] == "ATTR": 
                    if (liftValue < 1.01 and conditionProb < 0.98) or (liftValue == 1.0 and (conditionProb < 0.98 or statementProb != 1.0)):
                        countLift += 1
                        print("Dropped")
                        resultDict[rule] = "Lift"
                        continue
                if rule.split("####")[0] == "COMBO":
                    if "Associate" in rule.split("####")[1] or "Branch" in rule.split("####")[1]: 
                        if (liftValue < 1.01 and conditionProb < 0.3) or (liftValue == 1.0 and (conditionProb != 1.0 and statementProb != 1.0)):
                            countLift += 1
                            print("Dropped")
                            resultDict[rule] = "Lift"
                            continue
                    else:
                        if (liftValue < 1.01 and conditionProb < 0.7) or (liftValue == 1.0 and (conditionProb != 1.0 and statementProb != 1.0)):
                            countLift += 1
                            print("Dropped")
                            resultDict[rule] = "Lift"
                            continue
                        
                print("Accepted")
            except Exception as e:
                print("Something went wrong when calculating confidence and lift", e)
                continue
        countLeft += 1
        resultDict[rule] = "Accept"
        csvWriter.writerow(rule.split("####"))
    print("countConfidence", countConfidence, "countLift", countLift, "countLeft", countLeft)
    evalFileName = csvFileName[:-4] + "Eval.json"
    with open(evalFileName, 'w') as f:
        json.dump(resultDict, f, sort_keys = True, indent = 4)
    csvFile.close()
    csvFilteredFile.close()
    
def filterRuleExpression(jsonFileName, jsonFilteredFileName, inputDirName, outputDirName):
    print(jsonFileName, jsonFilteredFileName, inputDirName, outputDirName)
   
    try:
        planJsonData = json.load(open(f"{outputDirName}/plan.json", "r"))
        configJsonData = json.load(open(f"{outputDirName}/config.json", "r"))
        dependencyListJsonData = json.load(open(f"{outputDirName}/dependencyList.json", "r"))
        referencesPredDictJsonData = json.load(open(f"{outputDirName}/referencesPredDict.json", "r"))
        referencesSuccDictJsonData = json.load(open(f"{outputDirName}/referencesSuccDict.json", "r"))
        offspringDictJsonData = json.load(open(f"{outputDirName}/offspringDict.json", "r"))
        ancestorDictJsonData = json.load(open(f"{outputDirName}/ancestorDict.json", "r"))
        naiveAncestorDictJsonData = json.load(open(f"{outputDirName}/naiveAncestorDict.json", "r"))
        schemaDetailView = json.load(open(f"../schemaFiles/azurermKBSchemaDetailView.json", "r"))
        plan = planJsonData["result"][0]["expressions"][0]["value"]
        config = configJsonData["result"][0]["expressions"][0]["value"]
        dependencyList = dependencyListJsonData["result"][0]["expressions"][0]["value"]
        referencesPredDict = referencesPredDictJsonData["result"][0]["expressions"][0]["value"]
        referencesSuccDict = referencesSuccDictJsonData["result"][0]["expressions"][0]["value"]
        offspringDict = offspringDictJsonData["result"][0]["expressions"][0]["value"]
        ancestorDict = ancestorDictJsonData["result"][0]["expressions"][0]["value"]
        naiveAncestorDict = naiveAncestorDictJsonData["result"][0]["expressions"][0]["value"]
    except:
        print("Something went wrong during other rego processing!")
        return
    if len(dependencyList) >= 200:
        print("rego plan file too complex!")
        return
    
    jsonRuleData = json.load(open(f"{jsonFileName}", "r"))
    jsonRuleFilteredData = defaultdict(list)
    opType = jsonFileName.split("/")[-1][:-4]
    print("output dir name: ", outputDirName)
    print("operation type: ", opType)
    repoImportance = json.load(open(f"../regoFiles/repoImportanceView.json", "r"))
    
    for row in jsonRuleData:
        if row[0] == "Operator":
            continue
        operationList = row[1].split("If")
        operationList = operationList[0].split("Then")
        rowIndex = 2
        if len(operationList) != 2:
            continue
        valueDict = defaultdict(list)
        topoDict1, topoDict2 = defaultdict(list), defaultdict(list)
        flagHandled = True
        for operation in operationList:
            if operation not in ["Absence", "Existence", "Constant", "Equal", "Unequal", "CIDRInclude", "CIDRExclude", \
                                "EqualCombo", "UnequalCombo", "CIDRIncludeCombo", "CIDRExcludeCombo", "BinConstantCombo", \
                                "AbsenceComboUp", "ExistenceComboUp", "AbsenceComboDown", "ExistenceComboDown", \
                                "ConstantComboUp", "ConstantComboDown", "Reference", "Branch", "Associate", "Negation", \
                                "Exclusive", "ConflictChild", "Intra", "AncestorReference", "AncestorBranch", "AncestorAssociate", "AncestorConflictChild", \
                                "CountChild", "CountParent", "Enum", "EnumComboDown", "EnumComboUp", "CIDRMask", "CIDRMaskComboDown", "CIDRMaskComboUp"]:
                flagHandled = False
                break
            if rowIndex == 2:
                rowIndex, valueDict, flagDiscard = positiveValidation(operation, opType, row, rowIndex, plan, config, dependencyList, \
                                                    referencesPredDict, referencesSuccDict, offspringDict, naiveAncestorDict, valueDict, topoDict1, operationList, repoImportance, schemaDetailView)
                if flagDiscard == True:
                    break
            else:
                rowIndex, valueDict, flagDiscard = positiveValidation(operation, opType, row, rowIndex, plan, config, dependencyList, \
                                                    referencesPredDict, referencesSuccDict, offspringDict, naiveAncestorDict, valueDict, topoDict2, operationList, repoImportance, schemaDetailView)
                if flagDiscard == True:
                    break
            
            if flagDiscard == True:
                break
        if flagHandled == False or flagDiscard == True:
            #print("Something went wrong during operation processing!", operationList)
            continue
        
        flagAttr = False
        countInvalid, countValid = 0, 0
        countConditionPositive, countStatementPositive, countJointPositive = 0, 0, 0
        countConditionNegative, countStatementNegative, countJointNegative = 0, 0, 0
        if operationList[0] in ["ConflictChild", "Exclusive"] and operationList[1] in ["ConflictChild", "Exclusive", "Reference"]:
            countInvalid = 1
        elif operationList[0] in ["Reference", "Branch", "Associate", "Exclusive", "ConflictChild", "Intra", "Negation", \
                                "AncestorReference", "AncestorConflictChild", "AncestorBranch", "AncestorAssociate"] and \
           operationList[1] in ["Reference", "Branch", "Associate", "Exclusive", "ConflictChild", "Intra", "Negation", \
                                "AncestorReference", "AncestorConflictChild", "AncestorBranch", "AncestorAssociate"]:
                ### Handling TOPO combinations, so that we can process cases where both condition and statement are TOPO operators.
                valueDict = defaultdict(list)
                keyIndex = 0 
                for key1 in list(topoDict1.keys()):
                    flagViolation = True
                    for key2 in list(topoDict2.keys()):
                        if "Negation" in operationList:
                            if key1[:1] == key2[:1]:
                                flagViolation = False
                                keyIndex += 1
                                valueDict[keyIndex] = topoDict1[key1][:] + topoDict2[key2][:]
                        else:
                            if key1[:2] == key2[:2]:
                                flagViolation = False
                                keyIndex += 1
                                valueDict[keyIndex] = topoDict1[key1][:] + topoDict2[key2][:]
                    if flagViolation == True:
                        countInvalid += 1
                        
                        
        elif operationList[0] in ["EnumComboDown", "CountChild"] and operationList[1] in ["EnumComboDown", "CountChild"] :
            countInvalid = 1
        elif operationList[0] in ["EnumComboUp", "CountParent"] and operationList[1] in ["EnumComboUp", "CountParent"] :
            countInvalid = 1
        elif operationList[0] in ["Enum", "EnumComboDown", "EnumComboUp"] and \
             operationList[1] in ["CountChild", "CountParent", "CIDRMask", "CIDRMaskComboDown", "CIDRMaskComboUp", "Enum"]:
            countInvalid = 0
        elif operationList[0] in ["CountChild", "CountParent", "Enum", "CIDRMask", "EnumComboDown", "EnumComboUp", "CIDRMaskComboDown", "CIDRMaskComboUp"] or \
             operationList[1] in ["CountChild", "CountParent", "Enum", "CIDRMask", "EnumComboDown", "EnumComboUp", "CIDRMaskComboDown", "CIDRMaskComboUp"]:
            countInvalid = 1
        elif operationList[0] in ["Exclusive", "ConflictChild", "AncestorConflictChild"] and \
             operationList[1] in [ "EqualCombo", "UnequalCombo", "CIDRIncludeCombo", "CIDRExcludeCombo", "BinConstantCombo", \
                                "AbsenceComboUp", "ExistenceComboUp", "AbsenceComboDown", "ExistenceComboDown", \
                                "ConstantComboUp", "ConstantComboDown"]:
            countInvalid = 1
        elif operationList[1] in ["Exclusive", "ConflictChild", "AncestorConflictChild"] and \
             operationList[0] in [ "EqualCombo", "UnequalCombo", "CIDRIncludeCombo", "CIDRExcludeCombo", "BinConstantCombo", \
                                "AbsenceComboUp", "ExistenceComboUp", "AbsenceComboDown", "ExistenceComboDown", \
                                "ConstantComboUp", "ConstantComboDown"]:
            countInvalid = 1
        else:     
            if row[0] == "ATTR" or row[0] == "COMBO":
                flagAttr = True          
            for key in valueDict:
                if len(valueDict[key]) != 2:
                    continue
                if not (valueDict[key][0] == False or valueDict[key][1] == True):
                    countInvalid += 1
                else:
                    countValid += 1
                if valueDict[key][0] == True:
                    countConditionPositive += 1
                else:
                    countConditionNegative += 1
                if valueDict[key][1] == True:
                    countStatementPositive += 1
                else:
                    countStatementNegative += 1
                if valueDict[key][0] == True and valueDict[key][1] == True:
                    countJointPositive += 1
                else:
                    countJointNegative += 1
                # elif valueDict[key][0] == False and valueDict[key][1] == True:
                #     countInvalid += 1
        newRow = []
        for item in row:
            if item != "":
                newRow.append(item)
        if countInvalid == 0:
            jsonRuleFilteredData["####".join(newRow)] =[True, countConditionPositive, countConditionNegative, \
                                 countStatementPositive, countStatementNegative, countJointPositive, countJointNegative, flagAttr]
        else:
            jsonRuleFilteredData["####".join(newRow)] = [False, countConditionPositive, countConditionNegative, \
                                 countStatementPositive, countStatementNegative, countJointPositive, countJointNegative, flagAttr]
    print("reached termination normaly")   
    with open(jsonFilteredFileName, 'w') as f:
        json.dump(jsonRuleFilteredData, f, sort_keys = True, indent = 4)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_file", help="the name of csv file to be translated")
    parser.add_argument("--rego_dir", help="the directory of rego files")
    args = parser.parse_args()
    return args

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource_type", help="the type of the resource we want to get")
    parser.add_argument("--operation_type", help="the type of the operation we want to extract")
    parser.add_argument("--reversed_type", help="whether to reverse the operation", nargs='?', default = "true")
    #parser.add_argument("--threshold", help="get rules ranked by frequency to a certain threshold", nargs='?', default = "200")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    if not os.path.exists(f"../ruleJsonFiles/"):
        os.mkdir(f"../ruleJsonFiles/")
    if args.resource_type == "TEST" and args.operation_type == "ALL":
        ### Usage Example: time python3 -u regoMVPRuleFilter.py --resource_type TEST --operation_type ALL > output6
        for resourceName in regoMVPGetKnowledgeBase.resourceList:
            for operator in ["ATTR", "COMBO", "TOPO"]:
                if not os.path.exists(f"../plainTextFiles/{resourceName}/"):
                    os.mkdir(f"../plainTextFiles/{resourceName}")
                if not os.path.exists(f"../ruleJsonFiles/{resourceName}/"):
                    os.mkdir(f"../ruleJsonFiles/{resourceName}")
                regoMVPRulePlainText.reverseRuleExpression(f"../csvFiles/{resourceName}/{operator}.csv", f"../csvFiles/{resourceName}/{operator}RE.csv")
                filterInBatch(resourceName, operator, f"../csvFiles/{resourceName}/{operator}.csv", f"../csvFiles/{resourceName}/{operator}FI.csv", f"../regoFiles/{resourceName}/outputRegoPlanHandledFormat", 16)
                filterInBatch(resourceName, operator+"RE", f"../csvFiles/{resourceName}/{operator}RE.csv", f"../csvFiles/{resourceName}/{operator}REFI.csv", f"../regoFiles/{resourceName}/outputRegoPlanHandledFormat", 16)
                #regoMVPRulePlainText.translateCSVtoFormats(f"../csvFiles/{resourceName}/{operator}.csv", f"../plainTextFiles/{resourceName}/{operator}.txt", f"../ruleJsonFiles/{resourceName}/{operator}CL.json")
                #regoMVPRulePlainText.translateCSVtoFormats(f"../csvFiles/{resourceName}/{operator}RE.csv", f"../plainTextFiles/{resourceName}/{operator}RE.txt", f"../ruleJsonFiles/{resourceName}/{operator}RECL.json")
                regoMVPRulePlainText.translateCSVtoFormats(f"../csvFiles/{resourceName}/{operator}FI.csv", f"../plainTextFiles/{resourceName}/{operator}FI.txt", f"../ruleJsonFiles/{resourceName}/{operator}FICL.json", f"../testFiles/candidateFile0.json")
                regoMVPRulePlainText.translateCSVtoFormats(f"../csvFiles/{resourceName}/{operator}REFI.csv", f"../plainTextFiles/{resourceName}/{operator}REFI.txt", f"../ruleJsonFiles/{resourceName}/{operator}REFICL.json", f"../testFiles/candidateFile0.json")
                regoMVPRuleInterpolate.interpolateOperators(f"../csvFiles/{resourceName}/{operator}FI.csv", f"../csvFiles/{resourceName}/{operator}IN.csv", f"../ruleJsonFiles/{resourceName}/{operator}IN.json")
                regoMVPRuleInterpolate.interpolateOperators(f"../csvFiles/{resourceName}/{operator}REFI.csv", f"../csvFiles/{resourceName}/{operator}REIN.csv", f"../ruleJsonFiles/{resourceName}/{operator}REIN.json")
                 
    else:
        ### Usage Example: time python3 -u regoMVPRuleFilter.py --resource_type azurerm_application_gateway --operation_type TOPO --reversed_type false > output7
        resourceName = str(args.resource_type)
        operator = str(args.operation_type)
        if not os.path.exists(f"../plainTextFiles/{resourceName}/"):
            os.mkdir(f"../plainTextFiles/{resourceName}")
        if not os.path.exists(f"../filterRuleExpressionInput/"):
            os.mkdir(f"../filterRuleExpressionInput")
        if not os.path.exists(f"../filterRuleExpressionOutput/"):
            os.mkdir(f"../filterRuleExpressionOutput")
        if not os.path.exists(f"../ruleJsonFiles/{resourceName}/"):
            os.mkdir(f"../ruleJsonFiles/{resourceName}")
        filterInBatch(resourceName, operator, f"../csvFiles/{resourceName}/{operator}.csv", f"../csvFiles/{resourceName}/{operator}FI.csv", f"../regoFiles/{resourceName}/outputRegoPlanHandledFormat", 16)
        regoMVPRulePlainText.translateCSVtoFormats(f"../csvFiles/{resourceName}/{operator}FI.csv", f"../plainTextFiles/{resourceName}/{operator}FI.txt", f"../ruleJsonFiles/{resourceName}/{operator}FICL.json", f"../testFiles/candidateFile0.json")
        regoMVPRuleInterpolate.interpolateOperators(f"../csvFiles/{resourceName}/{operator}FI.csv", f"../csvFiles/{resourceName}/{operator}IN.csv", f"../ruleJsonFiles/{resourceName}/{operator}IN.json")
        if str(args.reversed_type) == "true":
            regoMVPRulePlainText.reverseRuleExpression(f"../csvFiles/{resourceName}/{operator}.csv", f"../csvFiles/{resourceName}/{operator}RE.csv")
            filterInBatch(resourceName, operator+"RE", f"../csvFiles/{resourceName}/{operator}RE.csv", f"../csvFiles/{resourceName}/{operator}REFI.csv", f"../regoFiles/{resourceName}/outputRegoPlanHandledFormat", 16)
            regoMVPRulePlainText.translateCSVtoFormats(f"../csvFiles/{resourceName}/{operator}REFI.csv", f"../plainTextFiles/{resourceName}/{operator}REFI.txt", f"../ruleJsonFiles/{resourceName}/{operator}REFICL.json", f"../testFiles/candidateFile0.json")
            regoMVPRuleInterpolate.interpolateOperators(f"../csvFiles/{resourceName}/{operator}REFI.csv", f"../csvFiles/{resourceName}/{operator}REIN.csv", f"../ruleJsonFiles/{resourceName}/{operator}REIN.json")
