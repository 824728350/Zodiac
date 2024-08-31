from regoTemplateAttr import *
from regoTemplateTopo import *

opIfList = [
            ["Reference", opIfReference, idTypeIfReference, addressIfReference, pathIfReference, idAttrIfReference, attrSliceIfReference, outputIfReference], \
            ["Negation", opIfNegation, idTypeIfNegation, addressIfNegation, pathIfNegation, idAttrIfNegation, attrSliceIfNegation, outputIfNegation], \
            ["Associate", opIfAssociate, idTypeIfAssociate, addressIfAssociate, pathIfAssociate, idAttrIfAssociate, attrSliceIfAssociate, outputIfAssociate], \
            ["Branch", opIfBranch, idTypeIfBranch, addressIfBranch, pathIfBranch, idAttrIfBranch, attrSliceIfBranch, outputIfBranch], \
            ["CountChild", opIfCountChild, idTypeIfCountChild, addressIfCountChild, pathIfCountChild, idAttrIfCountChild, attrSliceIfCountChild, outputIfCountChild], \
            ["CountParent", opIfCountParent, idTypeIfCountParent, addressIfCountParent, pathIfCountParent, idAttrIfCountParent, attrSliceIfCountParent, outputIfCountParent], \
            ["Exclusive", opIfExclusive, idTypeIfExclusive, addressIfExclusive, pathIfExclusive, idAttrIfExclusive, attrSliceIfExclusive, outputIfExclusive], \
            ["ConflictChild", opIfConflictChild, idTypeIfConflictChild, addressIfConflictChild, pathIfConflictChild, idAttrIfConflictChild, attrSliceIfConflictChild, outputIfConflictChild], \
            ["Intra", opIfIntra, idTypeIfIntra, addressIfIntra, pathIfIntra, idAttrIfIntra, attrSliceIfIntra, outputIfIntra], \
           ]

opThenList = [
              ["Absence", opThenAbsence, idTypeThenAbsence, addressThenAbsence, pathThenAbsence, idAttrThenAbsence, attrSliceThenAbsence, outputThenAbsence], \
              ["Existence", opThenExistence, idTypeThenExistence, addressThenExistence, pathThenExistence, idAttrThenExistence, attrSliceThenExistence, outputThenExistence], \
              ["Constant", opThenConstant, idTypeThenConstant, addressThenConstant, pathThenConstant, idAttrThenConstant, attrSliceThenConstant, outputThenConstant], \
              ["Equal", opThenEqual, idTypeThenEqual, addressThenEqual, pathThenEqual, idAttrThenEqual, attrSliceThenEqual, outputThenEqual], \
              ["Unequal", opThenUnequal, idTypeThenUnequal, addressThenUnequal, pathThenUnequal, idAttrThenUnequal, attrSliceThenUnequal, outputThenUnequal], \
              ["CIDRInclude", opThenCIDRInclude, idTypeThenCIDRInclude, addressThenCIDRInclude, pathThenCIDRInclude, idAttrThenCIDRInclude, attrSliceThenCIDRInclude, outputThenCIDRInclude], \
              ["CIDRExclude", opThenCIDRExclude, idTypeThenCIDRExclude, addressThenCIDRExclude, pathThenCIDRExclude, idAttrThenCIDRExclude, attrSliceThenCIDRExclude, outputThenCIDRExclude], \
              ["Enum", opThenEnum, idTypeThenEnum, addressThenEnum, pathThenEnum, idAttrThenEnum, attrSliceThenEnum, outputThenEnum], \
              ["CIDRMask", opThenCIDRMask, idTypeThenCIDRMask, addressThenCIDRMask, pathThenCIDRMask, idAttrThenCIDRMask, attrSliceThenCIDRMask, outputThenCIDRMask], \
             ]

opComplexIfList = [
                   ["AncestorReference", opIfAncestorReference, idTypeIfAncestorReference, addressIfAncestorReference, pathIfAncestorReference, idAttrIfAncestorReference, attrSliceIfAncestorReference, outputIfAncestorReference], \
                   ["AncestorConflictChild", opIfAncestorConflictChild, idTypeIfAncestorConflictChild, addressIfAncestorConflictChild, pathIfAncestorConflictChild, idAttrIfAncestorConflictChild, attrSliceIfAncestorConflictChild, outputIfAncestorConflictChild], \
                   ["Peer", opIfPeer, idTypeIfPeer, addressIfPeer, pathIfPeer, idAttrIfPeer, attrSliceIfPeer, outputIfPeer], \
                   ["AncestorAssociate", opIfAncestorAssociate, idTypeIfAncestorAssociate, addressIfAncestorAssociate, pathIfAncestorAssociate, idAttrIfAncestorAssociate, attrSliceIfAncestorAssociate, outputIfAncestorAssociate], \
                   ["AncestorBranch", opIfAncestorBranch, idTypeIfAncestorBranch, addressIfAncestorBranch, pathIfAncestorBranch, idAttrIfAncestorBranch, attrSliceIfAncestorBranch, outputIfAncestorBranch], \
                 ]

opComplexThenList = [
                   ["BinConstant", opThenBinConstant, idTypeThenBinConstant, addressThenBinConstant, pathThenBinConstant, idAttrThenBinConstant, attrSliceThenBinConstant, outputThenBinConstant], \
                  ]
         
fuzzyList = ["CountChild", "CountParent", "Enum", "CIDRMask"]

def comboConstruction1(resourceType, providerType, item1, item2, regoOpString, opCombinations):
    
    opName1, opName2 = item1[0], item2[0]
    if (opName1 in fuzzyList and opName2 not in fuzzyList) or  (opName1 not in fuzzyList and opName2 in fuzzyList):
        if not (opName1 == "Reference" and opName2 == "CIDRMask"):
            return regoOpString, opCombinations
    if opName1 in ["Exclusive", "ConflictChild", "AncestorConflictChild"] and opName2 in ["Equal", "Unequal", "CIDRInclude", "CIDRExclude", "Constant", "Absence", "Existence"]:
        return regoOpString, opCombinations
    if opName1 in ["BinConstant"] or opName2 in ["BinConstant"]:
        return regoOpString, opCombinations
    idTypeList1, idTypeList2 = item1[2], item2[2]
    addressList1, addressList2 = item1[3], item2[3]
    # pathList1, pathList2 = item1[4], item2[4]
    idAttrList1, idAttrList2 = item1[5], item2[5]
    attrSliceList1, attrSliceList2 = item1[6], item2[6]
    output1, output2 = item1[7][0], item2[7][0]
    templateList = []
    address1, address2, address3, address4 = "", "", "", ""
    if opName1 in ["Reference", "Branch", "Exclusive", "Intra", "CountChild", "CountParent", \
                   "ConflictChild", "AncestorConflictChild", "AncestorReference", "Peer", "AncestorBranch"]:
        address1 = addressList1[0]
        address2 = addressList1[1]
    elif opName1 in ["Associate", "AncestorAssociate"]:
        address1 = addressList1[1]
        address2 = addressList1[2]
    elif opName1 in ["Negation"]:
        address1 = addressList1[0]
        address2 = addressList1[0]
    if opName2 in ["Equal", "Unequal", "CIDRInclude", "CIDRExclude", "BinConstant"]:
        address3 = addressList2[0]
        address4 = addressList2[1]
        templateList.append([opName2+"Combo", address1, address2, address3, address4])
    elif opName2 in ["Constant", "Existence", "Absence", "Enum", "CIDRMask"]:
        address3 = addressList2[0]
        if opName1 in ["Branch", "Associate", "AncestorAssociate", "AncestorBranch", "ConflictChild", "AncestorConflictChild", "Exclusive"]:
            return regoOpString, opCombinations
        templateList.append([opName2+"ComboDown", address1, "", address3, ""])
        if opName1 not in ["Negation"]:
            templateList.append([opName2+"ComboUp", address2, "", address3, ""])
    
    for template in templateList:
        opName2 = template[0]
        regoOpString += f"Combo{opName1}Then{opName2}List := [rule |\n"
        
        regoOpString += item1[1]
        idType1 = idTypeList1[0]
        regoOpString += f'    {idType1} == "{resourceType}"\n\n'
        address1 = template[1]
        address2 = template[2]
        address3 = template[3]
        address4 = template[4]
        if address1 != "" and address3 != "":
            regoOpString += f"    {address3} := {address1}\n"
        if address2 != "" and address4 != "":
            regoOpString += f"    {address4} := {address2}\n"
            
        for ele2 in range(len(addressList2)):
            idType2 = idTypeList2[ele2]
            address2 = addressList2[ele2]
            regoOpString += f'    {idType2} := resourceDict[{address2}][0]["type"]\n'
        for idType3 in idTypeList1[1:]:
            regoOpString += f'    contains({idType3}, "{providerType}")\n'
        for idType4 in idTypeList2[1:]:
            regoOpString += f'    contains({idType4}, "{providerType}")'
        
        regoOpString += item2[1] + "\n"
        
        ### Handling branch resource type constraints
        if opName1 == "Branch":
            idType1 = idTypeList1[0]
            idType2 = idTypeList1[1]
            regoOpString += f"    {idType1} == {idType2}\n"
            if opName2 == "EqualCombo" or opName2 == "CIDRIncludeCombo":
                address5 = addressList1[2]
                regoOpString += f'    not contains({address1}, "azurerm_resource_group")\n'
                regoOpString += f'    not contains({address5}, "azurerm_resource_group")\n'
            if opName2 == "UnequalCombo" or opName2 == "CIDRExcludeCombo":
                address5 = addressList1[2]
                regoOpString += f' any([contains({address5}, "azurerm_resource_group") == false, contains({address1}, "rule") == false])\n'
        if opName1 in ["Branch", "Associate", "AncestorBranch", "AncestorAssociate"] and opName2 == "EqualCombo":
            idAttr1 = idAttrList2[0]
            idAttr2 = idAttrList2[1]
            regoOpString += f"    any([{idAttr1} == {idAttr2}, contains({idAttr1}, {idAttr2}), contains({idAttr2}, {idAttr1})])\n"
        if opName1 == "AncestorBranch":
            address1 = addressList1[0]
            address2 = addressList1[1]
            regoOpString += f"    {address2} in artificialPredDict[{address1}]\n"
        if opName2 in ["EnumComboDown", "EnumComboUp"]:
            regoOpString += f'    count(attrThenEnum) == 1\n'  
        if opName2 in ["ConstantComboDown", "ExistenceComboDown", "AbsenceComboDown", "ConstantComboUp", "ExistenceComboUp", "AbsenceComboUp"]:
            attrSlice1 = attrSliceList2[0]
            regoOpString += f'    count({attrSlice1}) == 0\n'
        if opName2 in ["EqualCombo"]:
            attrSlice1 = attrSliceList2[0]
            regoOpString += f'    count({attrSlice1}) == 0\n'
        if opName1 in ["Reference"] and opName2 in ["UnequalCombo"]:
            idAttr1 = idAttrList2[0]
            idAttr2 = idAttrList2[1]
            type1 = idTypeList1[0]
            type2 = idTypeList1[1]
            regoOpString += f"    any([{type1} == {type2}, {idAttr1} != {idAttr2}])\n"
            regoOpString += f"    any([contains({idAttr1}, {idAttr2}), contains({idAttr2}, {idAttr1})])\n"
        regoOpString += f'    rule := concat(" ", ["{opName1}Then{opName2}", "####", '
        regoOpString += f'{output1}, "####", {output2}])\n'
        regoOpString += "]\n\n"
        opCombinations.append(f"Combo{opName1}Then{opName2}List")
        
    return regoOpString, opCombinations

### rule extraction mechansim for mining, targeting combo rules with both topology and attribute relations
def constructRegoCombo1(resourceType, opType):
    providerType = resourceType.split("_")[0]
    with open(f"../schemaFiles/{providerType}KBSchemaDetailView.json", "r") as f:
        resourceDetailString = f.read()
    with open(f"../regoFiles/repoView.json", "r") as f:
        resourceViewString = f.read()
    with open(f"../regoFiles/repoDefaultView.json", "r") as f:
        resourceDefaultViewString = f.read()
    with open(f"../regoFiles/repoDependencyView.json", "r") as f:
        resourceDependencyViewString = f.read()
    with open(f"../regoFiles/repoReferenceView.json", "r") as f:
        resourceReferenceViewString = f.read()
    with open(f"../regoFiles/repoImportanceView.json", "r") as f:
        resourceImportanceViewString = f.read()
    with open(f"../regoFiles/repoTrivialView.json", "r") as f:
        resourceTrivialViewString = f.read()
    with open(f"../schemaFiles/{providerType}KBSchemaCompleteView.json", "r") as f:
        resourceCompleteViewString = f.read()
        
    opCombinations = []
    regoOpString = ""
    for index1 in range(len(opIfList)):
        for index2 in range(len(opThenList)):
            item1 = opIfList[index1]
            item2 = opThenList[index2]
            
            regoOpString, opCombinations = comboConstruction1(resourceType, providerType, item1, item2, regoOpString, opCombinations)
            
    regoString = "resourceDetail := "+ resourceDetailString + "\n" + \
                 "resourceView := "+ resourceViewString + "\n" + \
                 "resourceDependencyView := "+ resourceDependencyViewString + "\n" + \
                 "resourceCompleteView := " + resourceCompleteViewString + "\n" + \
                 "resourceImportanceView := " + resourceImportanceViewString + "\n" + \
                 "resourceTrivialView := " + resourceTrivialViewString + "\n" + \
                 "resourceReferenceView :=" + resourceReferenceViewString + "\n" + \
                 "resourceDefaultView := "+ resourceDefaultViewString + "\n"+ regoOpString
    return regoString, opCombinations

### rule extraction mechansim for mining, targeting combo rules with complex conditions (case by case)
def constructRegoCombo2(resourceType, opType):
    providerType = resourceType.split("_")[0]
    with open(f"../schemaFiles/{providerType}KBSchemaDetailView.json", "r") as f:
        resourceDetailString = f.read()
    with open(f"../regoFiles/repoView.json", "r") as f:
        resourceViewString = f.read()
    with open(f"../regoFiles/repoDefaultView.json", "r") as f:
        resourceDefaultViewString = f.read()
    with open(f"../regoFiles/repoReferenceView.json", "r") as f:
        resourceReferenceViewString = f.read()
    with open(f"../regoFiles/repoImportanceView.json", "r") as f:
        resourceImportanceViewString = f.read()
    with open(f"../regoFiles/repoTrivialView.json", "r") as f:
        resourceTrivialViewString = f.read()
    with open(f"../regoFiles/repoDependencyView.json", "r") as f:
        resourceDependencyViewString = f.read()
    
    combinationList = [
                        ["AncestorReference", "Equal"], \
                        ["AncestorReference", "Constant"], \
                        ["AncestorBranch", "Constant"], \
                        ["Branch", "BinConstant"], \
                        ["AncestorAssociate", "CIDRExclude"], \
                        ["AncestorAssociate", "Equal"], \
                      ]
    opCombinations = []
    regoOpString = ""
    
    for combination in combinationList:
        opName1 = combination[0]
        opName2 = combination[1]
        item1, item2 = None, None
        for op in opIfList+opComplexIfList:
            if op[0] == opName1:
                item1 = op
        for op in opThenList+opComplexThenList:
            if op[0] == opName2:
                item2 = op
        if item1 != None and item2 != None:
            regoOpString, opCombinations = comboConstruction1(resourceType, providerType, item1, item2, regoOpString, opCombinations)
            
    regoString = "resourceDetail := "+ resourceDetailString + "\n" + \
                 "resourceView := "+ resourceViewString + "\n" + \
                 "resourceDependencyView := "+ resourceDependencyViewString + "\n" + \
                 "resourceImportanceView := " + resourceImportanceViewString + "\n" + \
                 "resourceTrivialView := " + resourceTrivialViewString + "\n" + \
                 "resourceReferenceView :=" + resourceReferenceViewString + "\n" + \
                 "resourceDefaultView := "+ resourceDefaultViewString + "\n"+ regoOpString
    return regoString, opCombinations