### Definition of dependency relation expressions, this is the corner stoner for both
### inter resource rules. If a rule contains dependency expressions in its statement, 
### then the rule could only be negated through topology changes.

### If resource1.reference1 depends on resource2.reference2
opIfReference = """
    addressIfReference1 := dependencyList[IfReferenceA][0]
    addressIfReference2 := dependencyList[IfReferenceA][1]
    idTypeIfReference1 := resourceDict[addressIfReference1][0]["type"]
    idTypeIfReference2 := resourceDict[addressIfReference2][0]["type"]
    idTypeIfReference1 in object.keys(resourceView)
    idTypeIfReference2 in object.keys(resourceView)
    #idTypeIfReference1 != idTypeIfReference2
    idAttrIfReference1 := dependencyList[IfReferenceA][2]
    idAttrIfReference2 := dependencyList[IfReferenceA][3]
    attrSliceIfReference1 := dependencyList[IfReferenceA][4]
    attrSliceIfReference2 := dependencyList[IfReferenceA][5]
"""
pathIfReference = ["IfReferenceA"]
idTypeIfReference = ["idTypeIfReference1", "idTypeIfReference2"]
addressIfReference = ["addressIfReference1", "addressIfReference2"]
idAttrIfReference = ["idAttrIfReference1", "idAttrIfReference2"]
attrSliceIfReference = ["attrSliceIfReference1", "attrSliceIfReference2"] 
outputIfReference = ['idTypeIfReference1, idAttrIfReference1, "String", "####", idTypeIfReference2, idAttrIfReference2, "String"']

### Then resource1.reference1 depends on resource2.reference2
opThenReference = """
    addressThenReference1 := dependencyList[ThenReferenceA][0]
    addressThenReference2 := dependencyList[ThenReferenceA][1]
    idTypeThenReference1 := resourceDict[addressThenReference1][0]["type"]
    idTypeThenReference2 := resourceDict[addressThenReference2][0]["type"]
    idTypeThenReference1 in object.keys(resourceView)
    idTypeThenReference2 in object.keys(resourceView)
    #idTypeThenReference1 != idTypeThenReference2
    idAttrThenReference1 := dependencyList[ThenReferenceA][2]
    idAttrThenReference2 := dependencyList[ThenReferenceA][3]
    attrSliceThenReference1 := dependencyList[ThenReferenceA][4]
    attrSliceThenReference2 := dependencyList[ThenReferenceA][5]
"""
pathThenReference = ["ThenReferenceA"]
idTypeThenReference = ["idTypeThenReference1", "idTypeThenReference2"]
addressThenReference = ["addressThenReference1", "addressThenReference2"]
idAttrThenReference = ["idAttrThenReference1", "idAttrThenReference2"]
attrSliceThenReference = ["attrSliceThenReference1", "attrSliceThenReference2"] 
outputThenReference = ['idTypeThenReference1, idAttrThenReference1, "String", "####", idTypeThenReference2, idAttrThenReference2, "String"']

### If resource1.reference1 DOES NOT depend on resource2.reference2
opIfNegation = """
    walk(resourceDict[addressIfNegation1][1]["values"], [pathIfNegation1, valueIfNegation1])
    idTypeIfNegation1 := resourceDict[addressIfNegation1][0]["type"]
    idTypeIfNegation2 := resourceDependencyView[idTypeIfNegation1][IfNegationA][1]
    idTypeIfNegation1 in object.keys(resourceView)
    idTypeIfNegation2 in object.keys(resourceView)
    attrIfNegation1 := [elemStr | elem := pathIfNegation1[n]; elemStr := sprintf("%v", [elem])]
    idAttrIfNegation1 := concat(".", attrIfNegation1)
    is_null(valueIfNegation1)
    idAttrIfNegation1 == resourceDependencyView[idTypeIfNegation1][IfNegationA][2]
    idAttrIfNegation2 := resourceDependencyView[idTypeIfNegation1][IfNegationA][3]
"""
pathIfNegation = ["pathIfNegation1"]
idTypeIfNegation = ["idTypeIfNegation1"]
addressIfNegation = ["addressIfNegation1"]
idAttrIfNegation = []
attrSliceIfNegation = [] 
outputIfNegation = ['idTypeIfNegation1, idAttrIfNegation1, "String", "####", idTypeIfNegation2, idAttrIfNegation2, "String"']

### Then resource1.reference1 DOES NOT depend on resource2.reference2
opThenNegation = """
    walk(resourceDict[addressThenNegation1][1]["values"], [pathThenNegation1, valueThenNegation1])
    idTypeThenNegation1 := resourceDict[addressThenNegation1][0]["type"]
    idTypeThenNegation2 := resourceDependencyView[idTypeThenNegation1][ThenNegationA][1]
    idTypeThenNegation1 in object.keys(resourceView)
    idTypeThenNegation2 in object.keys(resourceView)
    attrThenNegation1 := [elemStr | elem := pathThenNegation1[n]; elemStr := sprintf("%v", [elem])]
    idAttrThenNegation1 := concat(".", attrThenNegation1)
    is_null(valueThenNegation1)
    idAttrThenNegation1 == resourceDependencyView[idTypeThenNegation1][ThenNegationA][2]
    idAttrThenNegation2 := resourceDependencyView[idTypeThenNegation1][ThenNegationA][3]
"""
pathThenNegation = ["pathThenNegation1"]
idTypeThenNegation = ["idTypeThenNegation1"]
addressThenNegation = ["addressThenNegation1"]
idAttrThenNegation = []
attrSliceThenNegation = [] 
outputThenNegation = ['idTypeThenNegation1, idAttrThenNegation1, "String", "####", idTypeThenNegation2, idAttrThenNegation2, "String"']

### If resource1.reference1 associates with resource2.reference2 through resource3.reference3 and resource3.reference4
opIfAssociate = """
    addressIfAssociate1 := dependencyList[IfAssociateA][1]
    addressIfAssociate2 := dependencyList[IfAssociateB][1]
    addressIfAssociate3 := dependencyList[IfAssociateA][0]
    addressIfAssociate3 == dependencyList[IfAssociateB][0]
    #addressIfAssociate1 != addressIfAssociate2
    IfAssociateA != IfAssociateB
    not addressIfAssociate2 in referencesPredDict[addressIfAssociate1]
    not addressIfAssociate1 in referencesPredDict[addressIfAssociate2]
    idTypeIfAssociate1 := resourceDict[addressIfAssociate1][0]["type"]
    idTypeIfAssociate2 := resourceDict[addressIfAssociate2][0]["type"]
    idTypeIfAssociate3 := resourceDict[addressIfAssociate3][0]["type"]
    idTypeIfAssociate1 in object.keys(resourceView)
    idTypeIfAssociate2 in object.keys(resourceView)
    idTypeIfAssociate3 in object.keys(resourceView)
    idAttrIfAssociate3 := dependencyList[IfAssociateA][2]
    idAttrIfAssociate4 := dependencyList[IfAssociateB][2]
    idAttrIfAssociate1 := dependencyList[IfAssociateA][3]
    idAttrIfAssociate2 := dependencyList[IfAssociateB][3]
    idAttrIfAssociate3 <= idAttrIfAssociate4
    attrSliceIfAssociate3 := dependencyList[IfAssociateA][5]
    attrSliceIfAssociate4 := dependencyList[IfAssociateB][5]
    attrSliceIfAssociate1 := dependencyList[IfAssociateA][5]
    attrSliceIfAssociate2 := dependencyList[IfAssociateB][5]
"""
pathIfAssociate = ["IfAssociateA", "IfAssociateB"]
idTypeIfAssociate = ["idTypeIfAssociate3", "idTypeIfAssociate1", "idTypeIfAssociate2"]
addressIfAssociate = ["addressIfAssociate3", "addressIfAssociate1", "addressIfAssociate2"]
idAttrIfAssociate = ["idAttrIfAssociate1", "idAttrIfAssociate2", "idAttrIfAssociate3"]
attrSliceIfAssociate = ["attrSliceIfAssociate1", "attrSliceIfAssociate2", "attrSliceIfAssociate3", "attrSliceIfAssociate4"] 
outputIfAssociate = ['idTypeIfAssociate3, idAttrIfAssociate3, "String", "####", idTypeIfAssociate3, idAttrIfAssociate4, "String", "####", idTypeIfAssociate1, idAttrIfAssociate1, "String", "####", idTypeIfAssociate2, idAttrIfAssociate2, "String"']

### Then resource1.reference1 associates with resource2.reference2 through resource3.reference3 and resource3.reference4
opThenAssociate = """
    addressThenAssociate1 := dependencyList[ThenAssociateA][1]
    addressThenAssociate2 := dependencyList[ThenAssociateB][1]
    addressThenAssociate3 := dependencyList[ThenAssociateA][0]
    addressThenAssociate3 == dependencyList[ThenAssociateB][0]
    #addressThenAssociate1 != addressThenAssociate2
    ThenAssociateA != ThenAssociateB
    not addressThenAssociate2 in referencesPredDict[addressThenAssociate1]
    not addressThenAssociate1 in referencesPredDict[addressThenAssociate2]
    idTypeThenAssociate1 := resourceDict[addressThenAssociate1][0]["type"]
    idTypeThenAssociate2 := resourceDict[addressThenAssociate2][0]["type"]
    idTypeThenAssociate3 := resourceDict[addressThenAssociate3][0]["type"]
    idTypeThenAssociate1 in object.keys(resourceView)
    idTypeThenAssociate2 in object.keys(resourceView)
    idTypeThenAssociate3 in object.keys(resourceView)
    idAttrThenAssociate3 := dependencyList[ThenAssociateA][2]
    idAttrThenAssociate4 := dependencyList[ThenAssociateB][2]
    idAttrThenAssociate1 := dependencyList[ThenAssociateA][3]
    idAttrThenAssociate2 := dependencyList[ThenAssociateB][3]
    idAttrThenAssociate3 <= idAttrThenAssociate4
    attrSliceThenAssociate3 := dependencyList[ThenAssociateA][5]
    attrSliceThenAssociate4 := dependencyList[ThenAssociateB][5]
    attrSliceThenAssociate1 := dependencyList[ThenAssociateA][5]
    attrSliceThenAssociate2 := dependencyList[ThenAssociateB][5]
"""
pathThenAssociate = ["ThenAssociateA", "ThenAssociateB"]
idTypeThenAssociate = ["idTypeThenAssociate3", "idTypeThenAssociate1", "idTypeThenAssociate2"]
addressThenAssociate = ["addressThenAssociate3", "addressThenAssociate1", "addressThenAssociate2"]
idAttrThenAssociate = ["idAttrThenAssociate1", "idAttrThenAssociate2", "idAttrThenAssociate3"]
attrSliceThenAssociate = ["attrSliceThenAssociate1", "attrSliceThenAssociate2", "attrSliceThenAssociate3", "attrSliceThenAssociate4"] 
outputThenAssociate = ['idTypeThenAssociate3, idAttrThenAssociate3, "String", "####", idTypeThenAssociate3, idAttrThenAssociate4, "String", "####", idTypeThenAssociate1, idAttrThenAssociate1, "String", "####", idTypeThenAssociate2, idAttrThenAssociate2, "String"']

### If resource1.reference1 depends on resource3.reference3 and resource2.reference2 depends on resource3.reference4
opIfBranch = """
    addressIfBranch1 := dependencyList[IfBranchA][0]
    addressIfBranch2 := dependencyList[IfBranchB][0]
    addressIfBranch3 := dependencyList[IfBranchA][1]
    addressIfBranch3 == dependencyList[IfBranchB][1]
    IfBranchA != IfBranchB
    idTypeIfBranch1 := resourceDict[addressIfBranch1][0]["type"]
    idTypeIfBranch2 := resourceDict[addressIfBranch2][0]["type"]
    idTypeIfBranch3 := resourceDict[addressIfBranch3][0]["type"]
    idTypeIfBranch1 in object.keys(resourceView)
    idTypeIfBranch2 in object.keys(resourceView)
    idTypeIfBranch3 in object.keys(resourceView)
    # idTypeIfBranch1 == idTypeIfBranch2
    # addressIfBranch1 < addressIfBranch2
    idAttrIfBranch1 := dependencyList[IfBranchA][2]
    idAttrIfBranch2 := dependencyList[IfBranchB][2]
    idAttrIfBranch3 := dependencyList[IfBranchA][3]
    idAttrIfBranch4 := dependencyList[IfBranchB][3]
    idAttrIfBranch1 >= idAttrIfBranch2
    attrSliceIfBranch1 := dependencyList[IfBranchA][4]
    attrSliceIfBranch2 := dependencyList[IfBranchB][4]
    attrSliceIfBranch3 := dependencyList[IfBranchA][5]
    attrSliceIfBranch4 := dependencyList[IfBranchB][5]
"""
pathIfBranch = ["IfBranchA", "IfBranchB"]
idTypeIfBranch = ["idTypeIfBranch1", "idTypeIfBranch2", "idTypeIfBranch3"]
addressIfBranch = ["addressIfBranch1", "addressIfBranch2", "addressIfBranch3"]
idAttrIfBranch = ["idAttrIfBranch1", "idAttrIfBranch2", "idAttrIfBranch3", "idAttrIfBranch4"]
attrSliceIfBranch = ["attrSliceIfBranch1", "attrSliceIfBranch2", "attrSliceIfBranch3", "attrSliceIfBranch4"] 
outputIfBranch = ['idTypeIfBranch1, idAttrIfBranch1, "String", "####", idTypeIfBranch2, idAttrIfBranch2, "String", "####", idTypeIfBranch3, idAttrIfBranch3, "String", "####", idTypeIfBranch3, idAttrIfBranch4, "String"']

### Then resource1.reference1 depends on resource3.reference3 and resource2.reference2 depends on resource3.reference4
opThenBranch = """
    addressThenBranch1 := dependencyList[ThenBranchA][0]
    addressThenBranch2 := dependencyList[ThenBranchB][0]
    addressThenBranch3 := dependencyList[ThenBranchA][1]
    addressThenBranch3 == dependencyList[ThenBranchB][1]
    ThenBranchA != ThenBranchB
    idTypeThenBranch1 := resourceDict[addressThenBranch1][0]["type"]
    idTypeThenBranch2 := resourceDict[addressThenBranch2][0]["type"]
    idTypeThenBranch3 := resourceDict[addressThenBranch3][0]["type"]
    idTypeThenBranch1 in object.keys(resourceView)
    idTypeThenBranch2 in object.keys(resourceView)
    idTypeThenBranch3 in object.keys(resourceView)
    # idTypeThenBranch1 == idTypeThenBranch2
    # addressThenBranch1 < addressThenBranch2
    idAttrThenBranch1 := dependencyList[ThenBranchA][2]
    idAttrThenBranch2 := dependencyList[ThenBranchB][2]
    idAttrThenBranch1 <= idAttrThenBranch2
    idAttrThenBranch3 := dependencyList[ThenBranchA][3]
    idAttrThenBranch4 := dependencyList[ThenBranchB][3]
    attrSliceThenBranch1 := dependencyList[ThenBranchA][4]
    attrSliceThenBranch2 := dependencyList[ThenBranchB][4]
    attrSliceThenBranch3 := dependencyList[ThenBranchA][5]
    attrSliceThenBranch4 := dependencyList[ThenBranchB][5]
"""
pathThenBranch = ["ThenBranchA", "ThenBranchB"]
idTypeThenBranch = ["idTypeThenBranch1", "idTypeThenBranch2", "idTypeThenBranch3"]
addressThenBranch = ["addressThenBranch1", "addressThenBranch2", "addressThenBranch3"]
idAttrThenBranch = ["idAttrThenBranch1", "idAttrThenBranch2", "idAttrThenBranch3", "idAttrThenBranch4"]
attrSliceThenBranch = ["attrSliceThenBranch1", "attrSliceThenBranch2", "attrSliceThenBranch3", "attrSliceThenBranch4"] 
outputThenBranch = ['idTypeThenBranch1, idAttrThenBranch1, "String", "####", idTypeThenBranch2, idAttrThenBranch2, "String", "####", idTypeThenBranch3, idAttrThenBranch3, "String", "####", idTypeThenBranch3, idAttrThenBranch4, "String"']

### If multiple instances of resource1 depends on resource2.reference2
opIfCountChild = """
    addressIfCountChild1 := dependencyList[IfCountChildA][0]
    addressIfCountChild2 := dependencyList[IfCountChildA][1]
    idTypeIfCountChild1 := resourceDict[addressIfCountChild1][0]["type"]
    idTypeIfCountChild2 := resourceDict[addressIfCountChild2][0]["type"]
    idTypeIfCountChild1 in object.keys(resourceView)
    idTypeIfCountChild2 in object.keys(resourceView)
    idAttrIfCountChild1 := dependencyList[IfCountChildA][2]
    idAttrIfCountChild2 := dependencyList[IfCountChildA][3]
    addrListIfCountChild := [address | address in referencesSuccDict[addressIfCountChild2]; resourceDict[address][0]["type"] == idTypeIfCountChild1]
    #addrListIfCountChild := [address | address := dependencyList[n][0]; addressIfCountChild2 == dependencyList[n][1]; resourceDict[address][0]["type"] == idTypeIfCountChild1; idAttrIfCountChild1 == dependencyList[n][2]]
    addrNumIfCountChild := count(addrListIfCountChild)
    addrNumIfCountChild >= 2
    attrSliceIfCountChild1 := dependencyList[IfCountChildA][4]
    attrSliceIfCountChild2 := dependencyList[IfCountChildA][5]
"""
pathIfCountChild = ["IfCountChildA"]
idTypeIfCountChild = ["idTypeIfCountChild1", "idTypeIfCountChild2"]
addressIfCountChild = ["addressIfCountChild1", "addressIfCountChild2"]
idAttrIfCountChild = ["idAttrIfCountChild1", "idAttrIfCountChild2"]
attrSliceIfCountChild = ["attrSliceIfCountChild1", "attrSliceIfCountChild2"] 
outputIfCountChild = ['idTypeIfCountChild1, "PLACEHOLDER", "String", "####", idTypeIfCountChild2, "PLACEHOLDER", "String"']

### Then multiple instances of resource1 depends on resource2.reference2
opThenCountChild = """
    addressThenCountChild1 := dependencyList[ThenCountChildA][0]
    addressThenCountChild2 := dependencyList[ThenCountChildA][1]
    idTypeThenCountChild1 := resourceDict[addressThenCountChild1][0]["type"]
    idTypeThenCountChild2 := resourceDict[addressThenCountChild2][0]["type"]
    idTypeThenCountChild1 in object.keys(resourceView)
    idTypeThenCountChild2 in object.keys(resourceView)
    idAttrThenCountChild1 := dependencyList[ThenCountChildA][2]
    idAttrThenCountChild2 := dependencyList[ThenCountChildA][3]
    addrListThenCountChild := [address | address in referencesSuccDict[addressThenCountChild2]; resourceDict[address][0]["type"] == idTypeThenCountChild1]
    #addrListThenCountChild := [address | address := dependencyList[n][0]; addressThenCountChild2 == dependencyList[n][1]; resourceDict[address][0]["type"] == idTypeThenCountChild1; idAttrThenCountChild1 == dependencyList[n][2]]
    addrNumThenCountChild := count(addrListThenCountChild)
    addrNumThenCountChild >= 2
    attrSliceThenCountChild1 := dependencyList[ThenCountChildA][4]
    attrSliceThenCountChild2 := dependencyList[ThenCountChildA][5]
"""
pathThenCountChild = ["ThenCountChildA"]
idTypeThenCountChild = ["idTypeThenCountChild1", "idTypeThenCountChild2"]
addressThenCountChild = ["addressThenCountChild1", "addressThenCountChild2"]
idAttrThenCountChild = ["idAttrThenCountChild1", "idAttrThenCountChild2"]
attrSliceThenCountChild = ["attrSliceThenCountChild1", "attrSliceThenCountChild2"]
outputThenCountChild = ['idTypeThenCountChild1, "PLACEHOLDER", "String", "####", idTypeThenCountChild2, "PLACEHOLDER", "String"']

### If resource1 depends on multiple instances of resource2.reference2
opIfCountParent = """
    addressIfCountParent1 := dependencyList[IfCountParentA][0]
    addressIfCountParent2 := dependencyList[IfCountParentA][1]
    idTypeIfCountParent1 := resourceDict[addressIfCountParent1][0]["type"]
    idTypeIfCountParent2 := resourceDict[addressIfCountParent2][0]["type"]
    idTypeIfCountParent1 in object.keys(resourceView)
    idTypeIfCountParent2 in object.keys(resourceView)
    idAttrIfCountParent1 := dependencyList[IfCountParentA][2]
    idAttrIfCountParent2 := dependencyList[IfCountParentA][3]
    #addrListIfCountParent := [address | addressIfCountParent1 == dependencyList[n][0]; address := dependencyList[n][1]; resourceDict[address][0]["type"] == idTypeIfCountParent2; idAttrIfCountParent1 == dependencyList[n][2]]
    addrListIfCountParent := [address | address in referencesPredDict[addressIfCountParent1]; resourceDict[address][0]["type"] == idTypeIfCountParent2]
    addrNumIfCountParent := count(addrListIfCountParent)
    addrNumIfCountParent >= 2
    attrSliceIfCountParent1 := dependencyList[IfCountParentA][4]
    attrSliceIfCountParent2 := dependencyList[IfCountParentA][5]
"""
pathIfCountParent = ["IfCountParentA"]
idTypeIfCountParent = ["idTypeIfCountParent1", "idTypeIfCountParent2"]
addressIfCountParent = ["addressIfCountParent1", "addressIfCountParent2"]
idAttrIfCountParent = ["idAttrIfCountParent1", "idAttrIfCountParent2"]
attrSliceIfCountParent = ["attrSliceIfCountParent1", "attrSliceIfCountParent2"]
outputIfCountParent = ['idTypeIfCountParent1, "PLACEHOLDER", "String", "####", idTypeIfCountParent2, "PLACEHOLDER", "String"']

### Then resource1 depends on multiple instances of resource2.reference2
opThenCountParent = """
    addressThenCountParent1 := dependencyList[ThenCountParentA][0]
    addressThenCountParent2 := dependencyList[ThenCountParentA][1]
    idTypeThenCountParent1 := resourceDict[addressThenCountParent1][0]["type"]
    idTypeThenCountParent2 := resourceDict[addressThenCountParent2][0]["type"]
    idTypeThenCountParent1 in object.keys(resourceView)
    idTypeThenCountParent2 in object.keys(resourceView)
    idAttrThenCountParent1 := dependencyList[ThenCountParentA][2]
    idAttrThenCountParent2 := dependencyList[ThenCountParentA][3]
    #addrListThenCountParent := [address | addressThenCountParent1 == dependencyList[n][0]; address := dependencyList[n][1]; resourceDict[address][0]["type"] == idTypeThenCountParent2; idAttrThenCountParent1 == dependencyList[n][2]]
    addrListThenCountParent := [address | address in referencesPredDict[addressThenCountParent1]; resourceDict[address][0]["type"] == idTypeThenCountParent2]
    addrNumThenCountParent := count(addrListThenCountParent)
    addrNumThenCountParent >= 2
    attrSliceThenCountParent1 := dependencyList[ThenCountParentA][4]
    attrSliceThenCountParent2 := dependencyList[ThenCountParentA][5]
"""
pathThenCountParent = ["ThenCountParentA"]
idTypeThenCountParent = ["idTypeThenCountParent1", "idTypeThenCountParent2"]
addressThenCountParent = ["addressThenCountParent1", "addressThenCountParent2"]
idAttrThenCountParent = ["idAttrThenCountParent1", "idAttrThenCountParent2"]
attrSliceThenCountParent = ["attrSliceThenCountParent1", "attrSliceThenCountParent2"]
outputThenCountParent = ['idTypeThenCountParent1, "PLACEHOLDER", "String", "####", idTypeThenCountParent2, "PLACEHOLDER", "String"']

### If only resource1.reference1 depends on resource2.reference2
opIfExclusive = """
    addressIfExclusive1 := dependencyList[IfExclusiveA][0]
    addressIfExclusive2 := dependencyList[IfExclusiveA][1]
    idTypeIfExclusive1 := resourceDict[addressIfExclusive1][0]["type"]
    idTypeIfExclusive2 := resourceDict[addressIfExclusive2][0]["type"]
    idTypeIfExclusive1 in object.keys(resourceView)
    idTypeIfExclusive2 in object.keys(resourceView)
    #idAttrIfExclusive1 := dependencyList[IfExclusiveA][2]
    #idAttrIfExclusive2 := dependencyList[IfExclusiveA][3]
    addrListIfExclusive := [address | address := dependencyList[n][0]; addressIfExclusive2 == dependencyList[n][1]; address != addressIfExclusive1]
    addrNumIfExclusive := count(addrListIfExclusive)
    addrNumIfExclusive == 0
    #attrSliceIfExclusive1 := dependencyList[IfExclusiveA][4]
    #attrSliceIfExclusive2 := dependencyList[IfExclusiveA][5]
"""
pathIfExclusive = ["IfExclusiveA"]
idTypeIfExclusive = ["idTypeIfExclusive1", "idTypeIfExclusive2"]
addressIfExclusive = ["addressIfExclusive1", "addressIfExclusive2"]
idAttrIfExclusive = []
attrSliceIfExclusive = [] 
outputIfExclusive = ['idTypeIfExclusive1, "PLACEHOLDER", "String", "####", idTypeIfExclusive2, "PLACEHOLDER", "String"']

### Then only resource1.reference1 depends on resource2.reference2
opThenExclusive = """
    addressThenExclusive1 := dependencyList[ThenExclusiveA][0]
    addressThenExclusive2 := dependencyList[ThenExclusiveA][1]
    idTypeThenExclusive1 := resourceDict[addressThenExclusive1][0]["type"]
    idTypeThenExclusive2 := resourceDict[addressThenExclusive2][0]["type"]
    idTypeThenExclusive1 in object.keys(resourceView)
    idTypeThenExclusive2 in object.keys(resourceView)
    #idAttrThenExclusive1 := dependencyList[ThenExclusiveA][2]
    #idAttrThenExclusive2 := dependencyList[ThenExclusiveA][3]
    addrListThenExclusive := [address | address := dependencyList[n][0]; addressThenExclusive2 == dependencyList[n][1]; address != addressThenExclusive1]
    addrNumThenExclusive := count(addrListThenExclusive)
    addrNumThenExclusive == 0
    #attrSliceThenExclusive1 := dependencyList[ThenExclusiveA][4]
    #attrSliceThenExclusive2 := dependencyList[ThenExclusiveA][5]
"""
pathThenExclusive = ["ThenExclusiveA"]
idTypeThenExclusive = ["idTypeThenExclusive1", "idTypeThenExclusive2"]
addressThenExclusive = ["addressThenExclusive1", "addressThenExclusive2"]
idAttrThenExclusive = []
attrSliceThenExclusive = []
outputThenExclusive = ['idTypeThenExclusive1, "PLACEHOLDER", "String", "####", idTypeThenExclusive2, "PLACEHOLDER", "String"']

### If resource1.reference1 depends on resource2.reference2, then the other resource3 of the same type of resource1 cannot.
opIfConflictChild = """
    addressIfConflictChild1 := dependencyList[IfConflictChildA][0]
    addressIfConflictChild2 := dependencyList[IfConflictChildA][1]
    idTypeIfConflictChild1 := resourceDict[addressIfConflictChild1][0]["type"]
    idTypeIfConflictChild2 := resourceDict[addressIfConflictChild2][0]["type"]
    idTypeIfConflictChild1 in object.keys(resourceView)
    idTypeIfConflictChild2 in object.keys(resourceView)
    #idAttrIfConflictChild1 := dependencyList[IfConflictChildA][2]
    #idAttrIfConflictChild2 := dependencyList[IfConflictChildA][3]
    addrListIfConflictChild := [address | address := dependencyList[n][0]; addressIfConflictChild2 == dependencyList[n][1]; address != addressIfConflictChild1; resourceDict[address][0]["type"] == idTypeIfConflictChild1]
    addrNumIfConflictChild := count(addrListIfConflictChild)
    addrNumIfConflictChild == 0
    #attrSliceIfConflictChild1 := dependencyList[IfConflictChildA][4]
    #attrSliceIfConflictChild2 := dependencyList[IfConflictChildA][5]
"""
pathIfConflictChild = ["IfConflictChildA"]
idTypeIfConflictChild = ["idTypeIfConflictChild1", "idTypeIfConflictChild2"]
addressIfConflictChild = ["addressIfConflictChild1", "addressIfConflictChild2"]
idAttrIfConflictChild = []
attrSliceIfConflictChild = [] 
outputIfConflictChild = ['idTypeIfConflictChild1, "PLACEHOLDER", "String", "####", idTypeIfConflictChild2, "PLACEHOLDER", "String"']

### Then resource1.reference1 depends on resource2.reference2, then the other resource3 of the same type of resource1 cannot.
opThenConflictChild = """
    addressThenConflictChild1 := dependencyList[ThenConflictChildA][0]
    addressThenConflictChild2 := dependencyList[ThenConflictChildA][1]
    idTypeThenConflictChild1 := resourceDict[addressThenConflictChild1][0]["type"]
    idTypeThenConflictChild2 := resourceDict[addressThenConflictChild2][0]["type"]
    idTypeThenConflictChild1 in object.keys(resourceView)
    idTypeThenConflictChild2 in object.keys(resourceView)
    #idAttrThenConflictChild1 := dependencyList[ThenConflictChildA][2]
    #idAttrThenConflictChild2 := dependencyList[ThenConflictChildA][3]
    addrListThenConflictChild := [address | address := dependencyList[n][0]; addressThenConflictChild2 == dependencyList[n][1]; address != addressThenConflictChild1; resourceDict[address][0]["type"] == idTypeThenConflictChild1]
    addrNumThenConflictChild := count(addrListThenConflictChild)
    addrNumThenConflictChild == 0
    #attrSliceThenConflictChild1 := dependencyList[ThenConflictChildA][4]
    #attrSliceThenConflictChild2 := dependencyList[ThenConflictChildA][5]
"""
pathThenConflictChild = ["ThenConflictChildA"]
idTypeThenConflictChild = ["idTypeThenConflictChild1", "idTypeThenConflictChild2"]
addressThenConflictChild = ["addressThenConflictChild1", "addressThenConflictChild2"]
idAttrThenConflictChild = []
attrSliceThenConflictChild = []
outputThenConflictChild = ['idTypeThenConflictChild1, "PLACEHOLDER", "String", "####", idTypeThenConflictChild2, "PLACEHOLDER", "String"']

### If resource1.reference1 depends on resource2.reference3 and resource1.reference2 depends on resource2.reference4
opIfIntra = """
    addressIfIntra1 := dependencyList[IfIntraA][0]
    addressIfIntra2 := dependencyList[IfIntraA][1]
    addressIfIntra1 == dependencyList[IfIntraB][0]
    addressIfIntra2 == dependencyList[IfIntraB][1]
    IfIntraA != IfIntraB
    idTypeIfIntra1 := resourceDict[addressIfIntra1][0]["type"]
    idTypeIfIntra2 := resourceDict[addressIfIntra2][0]["type"]
    idTypeIfIntra1 in object.keys(resourceView)
    idTypeIfIntra2 in object.keys(resourceView)
    idAttrIfIntra1 := dependencyList[IfIntraA][2]
    idAttrIfIntra2 := dependencyList[IfIntraB][2]
    idAttrIfIntra3 := dependencyList[IfIntraA][3]
    idAttrIfIntra4 := dependencyList[IfIntraB][3]
    idAttrIfIntra1 <= idAttrIfIntra2
    #attrSliceIfIntra1 := dependencyList[IfIntraA][4]
    #attrSliceIfIntra2 := dependencyList[IfIntraB][4]
    #attrSliceIfIntra3 := dependencyList[IfIntraA][5]
    #attrSliceIfIntra4 := dependencyList[IfIntraB][5]
"""
pathIfIntra = ["IfIntraA", "IfIntraB"]
idTypeIfIntra = ["idTypeIfIntra1", "idTypeIfIntra2"]
addressIfIntra = ["addressIfIntra1", "addressIfIntra2"]
idAttrIfIntra = ["idAttrIfIntra1", "idAttrIfIntra2", "idAttrIfIntra3", "idAttrIfIntra4"]
#attrSliceIfIntra = ["attrSliceIfIntra1", "attrSliceIfIntra2", "attrSliceIfIntra3", "attrSliceIfIntra4"] 
attrSliceIfIntra = []
outputIfIntra = ['idTypeIfIntra1, idAttrIfIntra1, "String", "####", idTypeIfIntra1, idAttrIfIntra2, "String", "####", idTypeIfIntra2, idAttrIfIntra3, "String", "####", idTypeIfIntra2, idAttrIfIntra4, "String"']

### Then resource1.reference1 depends on resource2.reference3 and resource1.reference2 depends on resource2.reference4
opThenIntra = """
    addressThenIntra1 := dependencyList[ThenIntraA][0]
    addressThenIntra2 := dependencyList[ThenIntraA][1]
    addressThenIntra1 == dependencyList[ThenIntraB][0]
    addressThenIntra2 == dependencyList[ThenIntraB][1]
    ThenIntraA != ThenIntraB
    idTypeThenIntra1 := resourceDict[addressThenIntra1][0]["type"]
    idTypeThenIntra2 := resourceDict[addressThenIntra2][0]["type"]
    idTypeThenIntra1 in object.keys(resourceView)
    idTypeThenIntra2 in object.keys(resourceView)
    idAttrThenIntra1 := dependencyList[ThenIntraA][2]
    idAttrThenIntra2 := dependencyList[ThenIntraB][2]
    idAttrThenIntra3 := dependencyList[ThenIntraA][3]
    idAttrThenIntra4 := dependencyList[ThenIntraB][3]
    idAttrThenIntra1 <= idAttrThenIntra2
    #attrSliceThenIntra1 := dependencyList[ThenIntraA][4]
    #attrSliceThenIntra2 := dependencyList[ThenIntraB][4]
    #attrSliceThenIntra3 := dependencyList[ThenIntraA][5]
    #attrSliceThenIntra4 := dependencyList[ThenIntraB][5]
"""
pathThenIntra = ["ThenIntraA", "ThenIntraB"]
idTypeThenIntra = ["idTypeThenIntra1", "idTypeThenIntra2"]
addressThenIntra = ["addressThenIntra1", "addressThenIntra2"]
idAttrThenIntra = ["idAttrThenIntra1", "idAttrThenIntra2", "idAttrThenIntra3", "idAttrThenIntra4"]
#attrSliceThenIntra = ["attrSliceThenIntra1", "attrSliceThenIntra2", "attrSliceThenIntra3", "attrSliceThenIntra4"]
attrSliceThenIntra = []
outputThenIntra = ['idTypeThenIntra1, idAttrThenIntra1, "String", "####", idTypeThenIntra1, idAttrThenIntra2, "String", "####", idTypeThenIntra2, idAttrThenIntra3, "String", "####", idTypeThenIntra2, idAttrThenIntra4, "String"']

### If resource1.reference1 peered with resource2.reference2 through resource3.reference3 and resource4.reference4
opIfPeer = """
    addressIfPeer3 := referencesPredDict[addressIfPeer1][IfPeerA1]
    addressIfPeer4 := referencesPredDict[addressIfPeer1][IfPeerA2]
    addressIfPeer3 != addressIfPeer4
    addressIfPeer3 == referencesPredDict[addressIfpeer2][IfPeerB1]
    addressIfPeer4 == referencesPredDict[addressIfPeer2][IfPeerB2]
    addressIfPeer1 != addressIfPeer2
    idTypeIfPeer1 := resourceDict[addressIfPeer1][0]["type"]
    idTypeIfPeer2 := resourceDict[addressIfPeer2][0]["type"]
    idTypeIfPeer1 == idTypeIfPeer2
    idTypeIfPeer3 := resourceDict[addressIfPeer3][0]["type"]
    idTypeIfPeer4 := resourceDict[addressIfPeer4][0]["type"]
    idTypeIfPeer3 == idTypeIfPeer4
"""
pathIfPeer = []
idTypeIfPeer = ["idTypeIfPeer1", "idTypeIfPeer2"]
addressIfPeer = ["addressIfPeer1", "addressIfPeer2"]
idAttrIfPeer = []
attrSliceIfPeer = [] 
outputIfPeer = ['idTypeIfPeer1, "PLACEHOLDER", "String", "####", idTypeIfPeer2, "PLACEHOLDER", "String"']

### Then resource1.reference1 peered with resource2.reference2 through resource3.reference3 and resource4.reference4
opThenPeer = """
    addressThenPeer3 := referencesPredDict[addressThenPeer1][ThenPeerA1]
    addressThenPeer4 := referencesPredDict[addressThenPeer1][ThenPeerA2]
    addressThenPeer3 != addressThenPeer4
    addressThenPeer3 == referencesPredDict[addressThenpeer2][ThenPeerB1]
    addressThenPeer4 == referencesPredDict[addressThenPeer2][ThenPeerB2]
    addressThenPeer1 != addressThenPeer2
    idTypeThenPeer1 := resourceDict[addressThenPeer1][0]["type"]
    idTypeThenPeer2 := resourceDict[addressThenPeer2][0]["type"]
    idTypeThenPeer1 == idTypeThenPeer2
    idTypeThenPeer3 := resourceDict[addressThenPeer3][0]["type"]
    idTypeThenPeer4 := resourceDict[addressThenPeer4][0]["type"]
    idTypeThenPeer3 == idTypeThenPeer4
"""
pathThenPeer = []
idTypeThenPeer = ["idTypeThenPeer1", "idTypeThenPeer2"]
addressThenPeer = ["addressThenPeer1", "addressThenPeer2"]
idAttrThenPeer = []
attrSliceThenPeer = []
outputThenPeer = ['idTypeThenPeer1, "PLACEHOLDER", "String", "####", idTypeThenPeer2, "PLACEHOLDER", "String"']

### If reference2 is the ancestor of reference1
opIfAncestorReference = """
    addressIfAncestorReference2 in naiveAncestorDict[addressIfAncestorReference1]
    idTypeIfAncestorReference1 := resourceDict[addressIfAncestorReference1][0]["type"]
    idTypeIfAncestorReference1 in object.keys(resourceView)
    idTypeIfAncestorReference2 := resourceDict[addressIfAncestorReference2][0]["type"]
    idTypeIfAncestorReference2 in object.keys(resourceView)
    not addressIfAncestorReference2 in referencesPredDict[addressIfAncestorReference1]
    addressIfAncestorReference1 != addressIfAncestorReference2
    idTypeIfAncestorReference1 != idTypeIfAncestorReference2
"""
pathIfAncestorReference = []
idTypeIfAncestorReference = ["idTypeIfAncestorReference1", "idTypeIfAncestorReference2"]
addressIfAncestorReference = ["addressIfAncestorReference1", "addressIfAncestorReference2"]
idAttrIfAncestorReference = []
attrSliceIfAncestorReference = [] 
outputIfAncestorReference = ['idTypeIfAncestorReference1, "PLACEHOLDER", "String", "####", idTypeIfAncestorReference2, "PLACEHOLDER", "String"']

### Then reference2 is the ancestor of reference1
opThenAncestorReference = """
    addressThenAncestorReference2 in naiveAncestorDict[addressThenAncestorReference1]
    idTypeThenAncestorReference1 := resourceDict[addressThenAncestorReference1][0]["type"]
    idTypeThenAncestorReference1 in object.keys(resourceView)
    idTypeThenAncestorReference2 := resourceDict[addressThenAncestorReference2][0]["type"]
    idTypeThenAncestorReference2 in object.keys(resourceView)
    not addressThenAncestorReference2 in referencesPredDict[addressThenAncestorReference1]
    addressThenAncestorReference1 != addressThenAncestorReference2
    idTypeThenAncestorReference1 != idTypeThenAncestorReference2
"""
pathThenAncestorReference = []
idTypeThenAncestorReference = ["idTypeThenAncestorReference1", "idTypeThenAncestorReference2"]
addressThenAncestorReference = ["addressThenAncestorReference1", "addressThenAncestorReference2"]
idAttrThenAncestorReference = []
attrSliceThenAncestorReference = [] 
outputThenAncestorReference = ['idTypeThenAncestorReference1, "PLACEHOLDER", "String", "####", idTypeThenAncestorReference2, "PLACEHOLDER", "String"']

### If resource1.reference1 is the offspring of resource2.reference2, then the other resource3 of the same type of resource1 cannot.
opIfAncestorConflictChild = """
    addressIfAncestorConflictChild2 in naiveAncestorDict[addressIfAncestorConflictChild1]
    idTypeIfAncestorConflictChild1 := resourceDict[addressIfAncestorConflictChild1][0]["type"]
    idTypeIfAncestorConflictChild1 in object.keys(resourceView)
    idTypeIfAncestorConflictChild2 := resourceDict[addressIfAncestorConflictChild2][0]["type"]
    idTypeIfAncestorConflictChild2 in object.keys(resourceView)
    not addressIfAncestorConflictChild2 in referencesPredDict[addressIfAncestorConflictChild1]
    addressIfAncestorConflictChild1 != addressIfAncestorConflictChild2
    idTypeIfAncestorConflictChild1 != idTypeIfAncestorConflictChild2
    addrListIfAncestorConflictChild := [address | address := offspringDict[addressIfAncestorConflictChild2][n]; address != addressIfAncestorConflictChild1; resourceDict[address][0]["type"] == idTypeIfAncestorConflictChild1]
    addrNumIfAncestorConflictChild := count(addrListIfAncestorConflictChild)
    addrNumIfAncestorConflictChild == 0
"""
pathIfAncestorConflictChild = []
idTypeIfAncestorConflictChild = ["idTypeIfAncestorConflictChild1", "idTypeIfAncestorConflictChild2"]
addressIfAncestorConflictChild = ["addressIfAncestorConflictChild1", "addressIfAncestorConflictChild2"]
idAttrIfAncestorConflictChild = []
attrSliceIfAncestorConflictChild = [] 
outputIfAncestorConflictChild = ['idTypeIfAncestorConflictChild1, "PLACEHOLDER", "String", "####", idTypeIfAncestorConflictChild2, "PLACEHOLDER", "String"']

### If resource1.reference1 is the offspring of resource2.reference2, then the other resource3 of the same type of resource1 cannot.
opThenAncestorConflictChild = """
    addressThenAncestorConflictChild2 in naiveAncestorDict[addressThenAncestorConflictChild1]
    idTypeThenAncestorConflictChild1 := resourceDict[addressThenAncestorConflictChild1][0]["type"]
    idTypeThenAncestorConflictChild1 in object.keys(resourceView)
    idTypeThenAncestorConflictChild2 := resourceDict[addressThenAncestorConflictChild2][0]["type"]
    idTypeThenAncestorConflictChild2 in object.keys(resourceView)
    not addressThenAncestorConflictChild2 in referencesPredDict[addressThenAncestorConflictChild1]
    addressThenAncestorConflictChild1 != addressThenAncestorConflictChild2
    idTypeThenAncestorConflictChild1 != idTypeThenAncestorConflictChild2
    addrListThenAncestorConflictChild := [address | address := offspringDict[addressThenAncestorConflictChild2][n]; address != addressThenAncestorConflictChild1; resourceDict[address][0]["type"] == idTypeThenAncestorConflictChild1]
    addrNumThenAncestorConflictChild := count(addrListThenAncestorConflictChild)
    addrNumThenAncestorConflictChild == 0
"""
pathThenAncestorConflictChild = []
idTypeThenAncestorConflictChild = ["idTypeThenAncestorConflictChild1", "idTypeThenAncestorConflictChild2"]
addressThenAncestorConflictChild = ["addressThenAncestorConflictChild1", "addressThenAncestorConflictChild2"]
idAttrThenAncestorConflictChild = []
attrSliceThenAncestorConflictChild = []
outputThenAncestorConflictChild = ['idTypeThenAncestorConflictChild1, "PLACEHOLDER", "String", "####", idTypeThenAncestorConflictChild2, "PLACEHOLDER", "String"']

### If resource1.reference1 associates with resource2.reference2 through resource3.reference3 and resource3.reference4
opIfAncestorAssociate = """
    addressIfAncestorAssociate1 in naiveAncestorDict[addressIfAncestorAssociate3]
    addressIfAncestorAssociate2 in naiveAncestorDict[addressIfAncestorAssociate3]
    idTypeIfAncestorAssociate1 := resourceDict[addressIfAncestorAssociate1][0]["type"]
    idTypeIfAncestorAssociate2 := resourceDict[addressIfAncestorAssociate2][0]["type"]
    idTypeIfAncestorAssociate1 <= idTypeIfAncestorAssociate2
    idTypeIfAncestorAssociate3 := resourceDict[addressIfAncestorAssociate3][0]["type"]
    not addressIfAncestorAssociate1 in referencesPredDict[addressIfAncestorAssociate3]
    #not addressIfAncestorAssociate2 in referencesPredDict[addressIfAncestorAssociate3]
    not addressIfAncestorAssociate2 in naiveAncestorDict[addressIfAncestorAssociate1]
    not addressIfAncestorAssociate1 in naiveAncestorDict[addressIfAncestorAssociate2]
    idTypeIfAncestorAssociate1 in object.keys(resourceView)
    idTypeIfAncestorAssociate2 in object.keys(resourceView)
    idTypeIfAncestorAssociate3 in object.keys(resourceView)
"""
pathIfAncestorAssociate = []
idTypeIfAncestorAssociate = ["idTypeIfAncestorAssociate3", "idTypeIfAncestorAssociate1", "idTypeIfAncestorAssociate2"]
addressIfAncestorAssociate = ["addressIfAncestorAssociate3", "addressIfAncestorAssociate1", "addressIfAncestorAssociate2"]
idAttrIfAncestorAssociate = []
attrSliceIfAncestorAssociate = [] 
outputIfAncestorAssociate = ['idTypeIfAncestorAssociate3, "PLACEHOLDER", "String", "####", idTypeIfAncestorAssociate3, "PLACEHOLDER", "String", "####", idTypeIfAncestorAssociate1, "PLACEHOLDER", "String", "####", idTypeIfAncestorAssociate2, "PLACEHOLDER", "String"']

opThenAncestorAssociate = """
    addressThenAncestorAssociate1 in naiveAncestorDict[addressThenAncestorAssociate3]
    addressThenAncestorAssociate2 in naiveAncestorDict[addressThenAncestorAssociate3]
    idTypeThenAncestorAssociate1 := resourceDict[addressThenAncestorAssociate1][0]["type"]
    idTypeThenAncestorAssociate2 := resourceDict[addressThenAncestorAssociate2][0]["type"]
    idTypeThenAncestorAssociate1 <= idTypeThenAncestorAssociate2
    idTypeThenAncestorAssociate3 := resourceDict[addressThenAncestorAssociate3][0]["type"]
    not addressThenAncestorAssociate1 in referencesPredDict[addressThenAncestorAssociate3]
    #not addressThenAncestorAssociate2 in referencesPredDict[addressThenAncestorAssociate3]
    not addressThenAncestorAssociate2 in naiveAncestorDict[addressThenAncestorAssociate1]
    not addressThenAncestorAssociate1 in naiveAncestorDict[addressThenAncestorAssociate2]
    idTypeThenAncestorAssociate1 in object.keys(resourceView)
    idTypeThenAncestorAssociate2 in object.keys(resourceView)
    idTypeThenAncestorAssociate3 in object.keys(resourceView)
"""
pathThenAncestorAssociate = []
idTypeThenAncestorAssociate = ["idTypeThenAncestorAssociate3", "idTypeThenAncestorAssociate1", "idTypeThenAncestorAssociate2"]
addressThenAncestorAssociate = ["addressThenAncestorAssociate3", "addressThenAncestorAssociate1", "addressThenAncestorAssociate2"]
idAttrThenAncestorAssociate = []
attrSliceThenAncestorAssociate = [] 
outputThenAncestorAssociate = ['idTypeThenAncestorAssociate3, "PLACEHOLDER", "String", "####", idTypeThenAncestorAssociate3, "PLACEHOLDER", "String", "####", idTypeThenAncestorAssociate1, "PLACEHOLDER", "String", "####", idTypeThenAncestorAssociate2, "PLACEHOLDER", "String"']

### If resourcd3 has resource1 and resource2
opIfAncestorBranch = """
    addressIfAncestorBranch3 in naiveAncestorDict[addressIfAncestorBranch1]
    addressIfAncestorBranch3 in naiveAncestorDict[addressIfAncestorBranch2]
    idTypeIfAncestorBranch1 := resourceDict[addressIfAncestorBranch1][0]["type"]
    idTypeIfAncestorBranch2 := resourceDict[addressIfAncestorBranch2][0]["type"]
    idTypeIfAncestorBranch3 := resourceDict[addressIfAncestorBranch3][0]["type"]
    idTypeIfAncestorBranch1 in object.keys(resourceView)
    idTypeIfAncestorBranch2 in object.keys(resourceView)
    idTypeIfAncestorBranch3 in object.keys(resourceView)
    not addressIfAncestorBranch2 in naiveAncestorDict[addressIfAncestorBranch1]
    not addressIfAncestorBranch1 in naiveAncestorDict[addressIfAncestorBranch2]
    #not addressIfAncestorBranch3 in referencesPredDict[addressIfAncestorBranch1]
    not addressIfAncestorBranch3 in referencesPredDict[addressIfAncestorBranch2]
"""
pathIfAncestorBranch = []
idTypeIfAncestorBranch = ["idTypeIfAncestorBranch1", "idTypeIfAncestorBranch2", "idTypeIfAncestorBranch3"]
addressIfAncestorBranch = ["addressIfAncestorBranch1", "addressIfAncestorBranch2", "addressIfAncestorBranch3"]
idAttrIfAncestorBranch = []
attrSliceIfAncestorBranch = [] 
outputIfAncestorBranch = ['idTypeIfAncestorBranch1, "PLACEHOLDER", "String", "####", idTypeIfAncestorBranch2, "PLACEHOLDER", "String", "####", idTypeIfAncestorBranch3, "PLACEHOLDER", "String", "####", idTypeIfAncestorBranch3, "PLACEHOLDER", "String"']

### Then resourcd3 has resource1 and resource2
opThenAncestorBranch = """
    addressThenAncestorBranch3 in naiveAncestorDict[addressThenAncestorBranch1]
    addressThenAncestorBranch3 in naiveAncestorDict[addressThenAncestorBranch2]
    idTypeThenAncestorBranch1 := resourceDict[addressThenAncestorBranch1][0]["type"]
    idTypeThenAncestorBranch2 := resourceDict[addressThenAncestorBranch2][0]["type"]
    idTypeThenAncestorBranch3 := resourceDict[addressThenAncestorBranch3][0]["type"]
    idTypeThenAncestorBranch1 in object.keys(resourceView)
    idTypeThenAncestorBranch2 in object.keys(resourceView)
    idTypeThenAncestorBranch3 in object.keys(resourceView)
    not addressThenAncestorBranch2 in naiveAncestorDict[addressThenAncestorBranch1]
    not addressThenAncestorBranch1 in naiveAncestorDict[addressThenAncestorBranch2]
    #not addressThenAncestorBranch3 in referencesPredDict[addressThenAncestorBranch1]
    not addressThenAncestorBranch3 in referencesPredDict[addressThenAncestorBranch2]
"""
pathThenAncestorBranch = []
idTypeThenAncestorBranch = ["idTypeThenAncestorBranch1", "idTypeThenAncestorBranch2", "idTypeThenAncestorBranch3"]
addressThenAncestorBranch = ["addressThenAncestorBranch1", "addressThenAncestorBranch2", "addressThenAncestorBranch3"]
idAttrThenAncestorBranch = []
attrSliceThenAncestorBranch = [] 
outputThenAncestorBranch = ['idTypeThenAncestorBranch1, "PLACEHOLDER", "String", "####", idTypeThenAncestorBranch2, "PLACEHOLDER", "String", "####", idTypeThenAncestorBranch3, "PLACEHOLDER", "String", "####", idTypeThenAncestorBranch3, "PLACEHOLDER", "String"']


opIfList = [
            ["Reference", opIfReference, idTypeIfReference, addressIfReference, pathIfReference, idAttrIfReference, attrSliceIfReference, outputIfReference], \
            ["AncestorReference", opIfAncestorReference, idTypeIfAncestorReference, addressIfAncestorReference, pathIfAncestorReference, idAttrIfAncestorReference, attrSliceIfAncestorReference, outputIfAncestorReference], \
            ["Negation", opIfNegation, idTypeIfNegation, addressIfNegation, pathIfNegation, idAttrIfNegation, attrSliceIfNegation, outputIfNegation], \
            ["Associate", opIfAssociate, idTypeIfAssociate, addressIfAssociate, pathIfAssociate, idAttrIfAssociate, attrSliceIfAssociate, outputIfAssociate], \
            ["AncestorAssociate", opIfAncestorAssociate, idTypeIfAncestorAssociate, addressIfAncestorAssociate, pathIfAncestorAssociate, idAttrIfAncestorAssociate, attrSliceIfAncestorAssociate, outputIfAncestorAssociate], \
            ["Intra", opIfIntra, idTypeIfIntra, addressIfIntra, pathIfIntra, idAttrIfIntra, attrSliceIfIntra, outputIfIntra], \
            ["Branch", opIfBranch, idTypeIfBranch, addressIfBranch, pathIfBranch, idAttrIfBranch, attrSliceIfBranch, outputIfBranch], \
            ["AncestorBranch", opIfAncestorBranch, idTypeIfAncestorBranch, addressIfAncestorBranch, pathIfAncestorBranch, idAttrIfAncestorBranch, attrSliceIfAncestorBranch, outputIfAncestorBranch], \
            ["CountChild", opIfCountChild, idTypeIfCountChild, addressIfCountChild, pathIfCountChild, idAttrIfCountChild, attrSliceIfCountChild, outputIfCountChild], \
            ["CountParent", opIfCountParent, idTypeIfCountParent, addressIfCountParent, pathIfCountParent, idAttrIfCountParent, attrSliceIfCountParent, outputIfCountParent], \
            ["ConflictChild", opIfConflictChild, idTypeIfConflictChild, addressIfConflictChild, pathIfConflictChild, idAttrIfConflictChild, attrSliceIfConflictChild, outputIfConflictChild], \
            ["Exclusive", opIfExclusive, idTypeIfExclusive, addressIfExclusive, pathIfExclusive, idAttrIfExclusive, attrSliceIfExclusive, outputIfExclusive], \
            ["AncestorConflictChild", opIfAncestorConflictChild, idTypeIfAncestorConflictChild, addressIfAncestorConflictChild, pathIfAncestorConflictChild, idAttrIfAncestorConflictChild, attrSliceIfAncestorConflictChild, outputIfAncestorConflictChild], \
           ]
    
opThenList = [
              ["Reference", opThenReference, idTypeThenReference, addressThenReference, pathThenReference, idAttrThenReference, attrSliceThenReference, outputThenReference], \
              ["AncestorReference", opThenAncestorReference, idTypeThenAncestorReference, addressThenAncestorReference, pathThenAncestorReference, idAttrThenAncestorReference, attrSliceThenAncestorReference, outputThenAncestorReference], \
              ["Negation", opThenNegation, idTypeThenNegation, addressThenNegation, pathThenNegation, idAttrThenNegation, attrSliceThenNegation, outputThenNegation], \
              ["Associate", opThenAssociate, idTypeThenAssociate, addressThenAssociate, pathThenAssociate, idAttrThenAssociate, attrSliceThenAssociate, outputThenAssociate], \
              ["AncestorAssociate", opThenAncestorAssociate, idTypeThenAncestorAssociate, addressThenAncestorAssociate, pathThenAncestorAssociate, idAttrThenAncestorAssociate, attrSliceThenAncestorAssociate, outputThenAncestorAssociate], \
              ["Intra", opThenIntra, idTypeThenIntra, addressThenIntra, pathThenIntra, idAttrThenIntra, attrSliceThenIntra, outputThenIntra], \
              ["Branch", opThenBranch, idTypeThenBranch, addressThenBranch, pathThenBranch, idAttrThenBranch, attrSliceThenBranch, outputThenBranch], \
              ["AncestorBranch", opThenAncestorBranch, idTypeThenAncestorBranch, addressThenAncestorBranch, pathThenAncestorBranch, idAttrThenAncestorBranch, attrSliceThenAncestorBranch, outputThenAncestorBranch], \
              ["CountChild", opThenCountChild, idTypeThenCountChild, addressThenCountChild, pathThenCountChild, idAttrThenCountChild, attrSliceThenCountChild, outputThenCountChild], \
              ["CountParent", opThenCountParent, idTypeThenCountParent, addressThenCountParent, pathThenCountParent, idAttrThenCountParent, attrSliceThenCountParent, outputThenCountParent], \
              ["ConflictChild", opThenConflictChild, idTypeThenConflictChild, addressThenConflictChild, pathThenConflictChild, idAttrThenConflictChild, attrSliceThenConflictChild, outputThenConflictChild], \
              ["Exclusive", opThenExclusive, idTypeThenExclusive, addressThenExclusive, pathThenExclusive, idAttrThenExclusive, attrSliceThenExclusive, outputThenExclusive], \
              ["AncestorConflictChild", opThenAncestorConflictChild, idTypeThenAncestorConflictChild, addressThenAncestorConflictChild, pathThenAncestorConflictChild, idAttrThenAncestorConflictChild, attrSliceThenAncestorConflictChild, outputThenAncestorConflictChild], \
             ]

def topoConstruction(resourceType, providerType, ifList, thenList, fuzzyList, regoAddString, opCombinations):
    for index1 in range(len(ifList)):
        for index2 in range(index1, len(thenList)):
            regoOpString = ""
            item1 = ifList[index1]
            item2 = thenList[index2]
            opName1, opName2 = item1[0], item2[0]
            
            if (opName1 in fuzzyList and opName2 not in fuzzyList) or  (opName1 not in fuzzyList and opName2 in fuzzyList):
                continue
            idTypeList1, idTypeList2 = item1[2], item2[2]
            addressList1, addressList2 = item1[3], item2[3]
            pathList1, pathList2 = item1[4], item2[4]
            output1, output2 = item1[7][0], item2[7][0]
            regoOpString += f"Topo{opName1}Then{opName2}List := [rule |\n" 
            regoOpString += item1[1]
            idType1 = idTypeList1[0]
            idType2 = idTypeList2[0]
            
            if opName1 in ["AncestorReference"] and opName2 in ["AncestorConflictChild"]:
                address10 = addressList1[0]
                address20 = addressList2[0]
                regoOpString += f"    {address20} := {address10}\n"
                address11 = addressList1[1]
                address21 = addressList2[1]
                regoOpString += f"    {address21} == {address11}\n" 
            elif opName1 in ["Associate"] and opName2 in ["AncestorBranch"]:
                address11 = addressList1[1]
                address12 = addressList1[2]
                address20 = addressList2[0]
                address21 = addressList2[1]
                regoOpString += f"    {address20} := {address11}\n"
                regoOpString += f"    {address21} := {address12}\n"
            regoOpString += f'    {idType1} == "{resourceType}"\n'
            regoOpString += item2[1] + "\n"
            
            if len(idTypeList1) >= 2:
                for idType3 in idTypeList1[1:]:
                    regoOpString += f'    contains({idType3}, "{providerType}")\n'
            if len(idTypeList2) >= 2:
                for idType4 in idTypeList2[1:]:
                    regoOpString += f'    contains({idType4}, "{providerType}")\n'
            
            ### Handling combination of reference and branch
            if opName1 in ["Reference"] and opName2 in ["AncetorBranch", "Branch", "ConflictChild", "Exclusive", "Intra"]:
                address10 = addressList1[0]
                address20 = addressList2[0]
                regoOpString += f"    {address10} == {address20}\n"
                address11 = addressList1[1]
                address21 = addressList2[1]
                regoOpString += f"    {address11} == {address21}\n" 
                if opName2 == "ConflictChild":
                    regoOpString += f'    not contains({address10}, "azurerm_resource_group")\n'
                    regoOpString += f'    not contains({address11}, "azurerm_resource_group")\n'
            elif  opName1 in ["AncestorReference"] and opName2 in ["Branch"]:
                address10 = addressList1[0]
                address20 = addressList2[0]
                regoOpString += f"    {address10} == {address20}\n"
                address11 = addressList1[1]
                address21 = addressList2[1]
                regoOpString += f"    {address11} == {address21}\n"
            elif opName1 in ["Reference"] and opName2 in ["Associate"]:
                address10 = addressList1[0]
                address20 = addressList2[0]
                regoOpString += f"    {address10} == {address20}\n"
                address11 = addressList1[1]
                address21 = addressList2[1]
                regoOpString += f"    {address11} == {address21}\n"
                
            elif opName1 in ["Associate"] and opName2 in ["Branch"]:
                address11 = addressList1[1]
                address12 = addressList1[2]
                address20 = addressList2[0]
                address21 = addressList2[1]
                regoOpString += f"    {address11} == {address20}\n"
                regoOpString += f"    {address12} == {address21}\n"
            elif opName1 in ["Associate"] and opName2 in ["AncestorBranch"]:
                address20 = addressList2[0]
                address22 = addressList2[2]
                regoOpString += f"    not {address22} in referencesPredDict[{address20}]\n"
            elif opName1 in ["Associate"] and opName2 in ["Intra"]:
                address10 = addressList1[0]
                address11 = addressList1[1]
                address12 = addressList1[2]
                address20 = addressList2[0]
                address21 = addressList2[1]
                regoOpString += f"    {address10} == {address20}\n"
                regoOpString += f"    {address11} == {address21}\n"
                regoOpString += f"    {address12} == {address21}\n"
            else:
                continue
                    
            regoOpString += f'    rule := concat(" ", ["{opName1}Then{opName2}", "####", '
            regoOpString += f'{output1}, "####", {output2}])\n'
            regoOpString += "]\n\n"
            regoAddString += regoOpString
            opCombinations.append(f"Topo{opName1}Then{opName2}List")
    return  regoAddString, opCombinations   

### rule extraction mechansim for mining, targeting topology dependency-only rules
def constructRegoTopo1(resourceType, opType):
    providerType = resourceType.split("_")[0]
    with open(f"../regoFiles/repoView.json", "r") as f:
        resourceViewString = f.read()
    with open(f"../regoFiles/repoDependencyView.json", "r") as f:
        resourceDependencyViewString = f.read()
    
    fuzzyList = ["CountChild", "CountParent", "Enum", "CIDRMask"]
    
    opCombinations = []
    regoOpString = ""
    regoOpString, opCombinations = topoConstruction(resourceType, providerType, opIfList, opThenList, fuzzyList, regoOpString, opCombinations)
    regoString = "resourceView := "+ resourceViewString + "\n" + \
                 "resourceDependencyView := "+ resourceDependencyViewString + "\n" + regoOpString
    return regoString, opCombinations
