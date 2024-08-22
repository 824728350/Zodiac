from regoTemplateAttr import *
from regoTemplateTopo import *

opIfList = [
            ["Absence", opIfAbsence, idTypeIfAbsence, addressIfAbsence, pathIfAbsence, idAttrIfAbsence, attrSliceIfAbsence, outputIfAbsence], \
            ["Existence", opIfExistence, idTypeIfExistence, addressIfExistence, pathIfExistence, idAttrIfExistence, attrSliceIfExistence, outputIfExistence], \
            ["Constant", opIfConstant, idTypeIfConstant, addressIfConstant, pathIfConstant, idAttrIfConstant, attrSliceIfConstant, outputIfConstant], \
            ["Equal", opIfEqual, idTypeIfEqual, addressIfEqual, pathIfEqual, idAttrIfEqual, attrSliceIfEqual, outputIfEqual], \
            ["Unequal", opIfUnequal, idTypeIfUnequal, addressIfUnequal, pathIfUnequal, idAttrIfUnequal, attrSliceIfUnequal, outputIfUnequal], \
            ["CIDRInclude", opIfCIDRInclude, idTypeIfCIDRInclude, addressIfCIDRInclude, pathIfCIDRInclude, idAttrIfCIDRInclude, attrSliceIfCIDRInclude, outputIfCIDRInclude], \
            ["CIDRExclude", opIfCIDRExclude, idTypeIfCIDRExclude, addressIfCIDRExclude, pathIfCIDRExclude, idAttrIfCIDRExclude, attrSliceIfCIDRExclude, outputIfCIDRExclude], \
            ["Enum", opIfEnum, idTypeIfEnum, addressIfEnum, pathIfEnum, idAttrIfEnum, attrSliceIfEnum, outputIfEnum], \
            ["CIDRMask", opIfCIDRMask, idTypeIfCIDRMask, addressIfCIDRMask, pathIfCIDRMask, idAttrIfCIDRMask, attrSliceIfCIDRMask, outputIfCIDRMask], \
           ]
         
def constructRegoSingle(resourceType, opType):
    providerType = resourceType.split("_")[0]
    with open(f"../schemaFiles/{providerType}KBSchemaDetailView.json", "r") as f:
        resourceDetailString = f.read()
    with open(f"../regoFiles/repoView.json", "r") as f:
        resourceViewString = f.read()
    with open(f"../regoFiles/repoDefaultView.json", "r") as f:
        resourceDefaultViewString = f.read()
    
    opCombinations = []
    regoOpString = ""
    for index1 in range(len(opIfList)):
        item1 = opIfList[index1]
        opName1 = item1[0]
        idTypeList1 = item1[2]
        addressList1 = item1[3]
        pathList1 = item1[4]
        idAttrList1 = item1[5]
        attrSliceList1 = item1[6]
        output1 = item1[7][0]
        regoOpString += f"Single{opName1}List := [rule |\n" 
        for ele1 in range(len(addressList1)):
            idType1 = idTypeList1[ele1]
            address1 = addressList1[ele1]
            regoOpString += f'    {idType1} := resourceDict[{address1}][0]["type"]\n'
            regoOpString += f'    {idType1} == "{resourceType}"\n'
        if opName1 in ["Absence", "Existence", "Constant", "Equal", "Unequal", "CIDRInclude", "CIDRExclude", "Enum", "CIDRMask"]:
            for ele1 in range(len(addressList1)-1):
                address1 = addressList1[ele1]
                address2 = addressList1[ele1+1]
                regoOpString += f"    {address1} == {address2}\n"
        regoOpString += item1[1] + "\n"
       
        ### Handling equality attribute constraints
        if opName1 in ["Equal"]:
            idAttr1 = idAttrList1[0]
            idAttr2 = idAttrList1[1]
            regoOpString += f"    {idAttr1} <= {idAttr2}\n"
        
        regoOpString += f'    rule := concat(" ", ["{opName1}", "####", '
        regoOpString += f'{output1}])\n'
        regoOpString += "]\n\n"
        opCombinations.append(f"Single{opName1}List")
    
    regoString = "resourceDetail := "+ resourceDetailString + "\n" + \
                 "resourceView := "+ resourceViewString + "\n" + \
                 "resourceDefaultView := "+ resourceDefaultViewString + "\n"+ regoOpString
    return regoString, opCombinations