### Definition of attribute relation expressions, this is the corner stone for both
### intra and inter resource rules. If a rule only contain attribute relations in its 
### conditions and statement, then it is an intra resource rule.

### If some attribute is absent, i.e. null or empty list
opIfAbsence = """
    walk(resourceDict[addressIfAbsence][1]["values"], [pathIfAbsence, valueIfAbsence])
    is_string(pathIfAbsence[count(pathIfAbsence)-1]) 
    attrIfAbsence := [elem | elem := pathIfAbsence[n]; is_string(elem)]
    idAttrIfAbsence := concat(".", attrIfAbsence)
    resourceDetail[idTypeIfAbsence][idAttrIfAbsence] != "required"
    any([resourceCompleteView[idTypeIfAbsence][idAttrIfAbsence] == "string", resourceCompleteView[idTypeIfAbsence][idAttrIfAbsence] == "number", resourceCompleteView[idTypeIfAbsence][idAttrIfAbsence] == "list", resourceCompleteView[idTypeIfAbsence][idAttrIfAbsence] == "block"])
    not idAttrIfAbsence in resourceDefaultView[idTypeIfAbsence]
    attrSliceIfAbsence := array.slice(attrIfAbsence, 0, count(attrIfAbsence)-1)
    count(attrSliceIfAbsence) == 0
    #any([is_null(valueIfAbsence), count(valueIfAbsence) == 0])
    any([is_array(valueIfAbsence), is_null(valueIfAbsence)])
    any([is_array(valueIfAbsence) == false, valueIfAbsence == []])
    validateIfAbsence2 := object.get(resourceView[idTypeIfAbsence], idAttrIfAbsence, [])
    count(validateIfAbsence2) <= 8
    any([idAttrIfAbsence in resourceTrivialView[idTypeIfAbsence], count(validateIfAbsence2) <= 1])
    #is_null(valueIfAbsence)
    not contains(idAttrIfAbsence, "tags")
    not contains(idAttrIfAbsence, "port")
    not contains(idAttrIfAbsence, "address_prefix")
    not contains(idAttrIfAbsence, "address_space")
    not contains(idAttrIfAbsence, "id")
    not contains(idAttrIfAbsence, "certificate")
    not contains(idAttrIfAbsence, "_name")
"""
pathIfAbsence = ["pathIfAbsence"]
idTypeIfAbsence = ["idTypeIfAbsence"]
addressIfAbsence = ["addressIfAbsence"]
idAttrIfAbsence = ["idAttrIfAbsence"]
attrSliceIfAbsence = ["attrSliceIfAbsence"] 
outputIfAbsence = ['idTypeIfAbsence, idAttrIfAbsence, "Absence"']

### Then some attribute is absent, i.e. null or empty list
opThenAbsence = """
    walk(resourceDict[addressThenAbsence][1]["values"], [pathThenAbsence, valueThenAbsence])
    is_string(pathThenAbsence[count(pathThenAbsence)-1]) 
    attrThenAbsence := [elem | elem := pathThenAbsence[n]; is_string(elem)]
    idAttrThenAbsence := concat(".", attrThenAbsence)
    resourceDetail[idTypeThenAbsence][idAttrThenAbsence] != "required"
    any([resourceCompleteView[idTypeThenAbsence][idAttrThenAbsence] == "string", resourceCompleteView[idTypeThenAbsence][idAttrThenAbsence] == "number", resourceCompleteView[idTypeThenAbsence][idAttrThenAbsence] == "list", resourceCompleteView[idTypeThenAbsence][idAttrThenAbsence] == "block"])
    not idAttrThenAbsence in resourceDefaultView[idTypeThenAbsence]
    attrSliceThenAbsence := array.slice(attrThenAbsence, 0, count(attrThenAbsence)-1)
    count(attrSliceThenAbsence) == 0
    #any([is_null(valueThenAbsence), count(valueThenAbsence) == 0])
    any([is_array(valueThenAbsence), is_null(valueThenAbsence)])
    any([is_array(valueThenAbsence) == false, valueThenAbsence == []])
    validateThenAbsence2 := object.get(resourceView[idTypeThenAbsence], idAttrThenAbsence, [])
    count(validateThenAbsence2) <= 8
    any([idAttrThenAbsence in resourceTrivialView[idTypeThenAbsence], count(validateThenAbsence2) <= 1])
    #is_null(valueThenAbsence)
    not contains(idAttrThenAbsence, "tags")
    not contains(idAttrThenAbsence, "port")
    not contains(idAttrThenAbsence, "address_prefix")
    not contains(idAttrThenAbsence, "address_space")
    not contains(idAttrThenAbsence, "id")
    not contains(idAttrThenAbsence, "certificate")
    not contains(idAttrThenAbsence, "_name")
"""
pathThenAbsence = ["pathThenAbsence"]
idTypeThenAbsence = ["idTypeThenAbsence"]
addressThenAbsence = ["addressThenAbsence"]
idAttrThenAbsence = ["idAttrThenAbsence"]
attrSliceThenAbsence = ["attrSliceThenAbsence"] 
outputThenAbsence = ['idTypeThenAbsence, idAttrThenAbsence, "Absence"']

### If some attribute exist, i.e. not null and not empty list
opIfExistence = """
    walk(resourceDict[addressIfExistence][1]["values"], [pathIfExistence, valueIfExistence])
    is_string(pathIfExistence[count(pathIfExistence)-1]) 
    attrIfExistence := [elem | elem := pathIfExistence[n]; is_string(elem)]
    idAttrIfExistence := concat(".", attrIfExistence)
    resourceDetail[idTypeIfExistence][idAttrIfExistence] != "required"
    any([resourceCompleteView[idTypeIfExistence][idAttrIfExistence] != "string", is_string(valueIfExistence)])
    any([resourceCompleteView[idTypeIfExistence][idAttrIfExistence] != "block", valueIfExistence != {}])
    any([resourceCompleteView[idTypeIfExistence][idAttrIfExistence] != "number", is_number(valueIfExistence)])
    any([resourceCompleteView[idTypeIfExistence][idAttrIfExistence] != "list", valueIfExistence != []])
    not idAttrIfExistence in resourceDefaultView[idTypeIfExistence]
    attrSliceIfExistence := array.slice(attrIfExistence, 0, count(attrIfExistence)-1)
    validateIfExistence2 := object.get(resourceView[idTypeIfExistence], idAttrIfExistence, [])
    count(validateIfExistence2) <= 8
    any([idAttrIfExistence in resourceTrivialView[idTypeIfExistence], count(validateIfExistence2) <= 1])
    not contains(idAttrIfExistence, "tags")
    not contains(idAttrIfExistence, "port")
    not contains(idAttrIfExistence, "address_prefix")
    not contains(idAttrIfExistence, "address_space")
    not contains(idAttrIfExistence, "id")
    not contains(idAttrIfExistence, "certificate")
    not contains(idAttrIfExistence, "_name")
"""
pathIfExistence = ["pathIfExistence"]
idTypeIfExistence = ["idTypeIfExistence"]
addressIfExistence = ["addressIfExistence"]
idAttrIfExistence= ["idAttrIfExistence"]
attrSliceIfExistence = ["attrSliceIfExistence"]
outputIfExistence = ['idTypeIfExistence, idAttrIfExistence, "Existence"'] 

### Then some attribute exist, i.e. not null and not empty list
opThenExistence = """
    walk(resourceDict[addressThenExistence][1]["values"], [pathThenExistence, valueThenExistence])
    is_string(pathThenExistence[count(pathThenExistence)-1]) 
    attrThenExistence := [elem | elem := pathThenExistence[n]; is_string(elem)]
    idAttrThenExistence := concat(".", attrThenExistence)
    resourceDetail[idTypeThenExistence][idAttrThenExistence] != "required"
    any([resourceCompleteView[idTypeThenExistence][idAttrThenExistence] != "string", is_string(valueThenExistence)])
    any([resourceCompleteView[idTypeThenExistence][idAttrThenExistence] != "block", valueThenExistence != {}])
    any([resourceCompleteView[idTypeThenExistence][idAttrThenExistence] != "number", is_number(valueThenExistence)])
    any([resourceCompleteView[idTypeThenExistence][idAttrThenExistence] != "list", valueThenExistence != []])
    not idAttrThenExistence in resourceDefaultView[idTypeThenExistence]
    attrSliceThenExistence := array.slice(attrThenExistence, 0, count(attrThenExistence)-1)
    validateThenExistence2 := object.get(resourceView[idTypeThenExistence], idAttrThenExistence, [])
    count(validateThenExistence2) <= 8
    any([idAttrThenExistence in resourceTrivialView[idTypeThenExistence], count(validateThenExistence2) <= 1])
    #not is_null(valueThenExistence)
    #not count(valueThenExistence) == 0
    not contains(idAttrThenExistence, "tags")
    not contains(idAttrThenExistence, "port")
    not contains(idAttrThenExistence, "address_prefix")
    not contains(idAttrThenExistence, "address_space")
    not contains(idAttrThenExistence, "id")
    not contains(idAttrThenExistence, "certificate")
    not contains(idAttrThenExistence, "_name")
"""
pathThenExistence = ["pathThenExistence"]
idTypeThenExistence = ["idTypeThenExistence"]
addressThenExistence = ["addressThenExistence"]
idAttrThenExistence= ["idAttrThenExistence"]
attrSliceThenExistence = ["attrSliceThenExistence"]
outputThenExistence = ['idTypeThenExistence, idAttrThenExistence, "Existence"']

### If attribute is certain constant in the filtered global knowledge base
opIfConstant = """
    walk(resourceDict[addressIfConstant][1]["values"], [pathIfConstant, valueIfConstant])
    attrIfConstant := [elem | elem := pathIfConstant[n]; is_string(elem)]
    idAttrIfConstant := concat(".", attrIfConstant)
    any([resourceDetail[idTypeIfConstant][idAttrIfConstant] == "required", idAttrIfConstant in resourceDefaultView[idTypeIfConstant], idAttrIfConstant in resourceImportanceView[idTypeIfConstant]])
    idAttrIfConstant != "location"
    not contains(idAttrIfConstant, "size")
    not contains(idAttrIfConstant, "offer")
    not contains(idAttrIfConstant, "publisher")
    not contains(idAttrIfConstant, "product")
    not contains(idAttrIfConstant, "zone")
    attrSliceIfConstant := array.slice(attrIfConstant, 0, count(attrIfConstant)-1)
    count(resourceView[idTypeIfConstant][idAttrIfConstant]) > 1
    count(resourceView[idTypeIfConstant][idAttrIfConstant]) <= 8
    valueIfConstant == resourceView[idTypeIfConstant][idAttrIfConstant][_]
    not is_null(valueIfConstant)
    not contains(idAttrIfConstant, "tags")
    not contains(idAttrIfConstant, "id")
    not contains(idAttrIfConstant, "_name")
    idValueIfConstant := sprintf("%v", [valueIfConstant])
"""
pathIfConstant = ["pathIfConstant"]
idTypeIfConstant = ["idTypeIfConstant"]
addressIfConstant = ["addressIfConstant"]
idAttrIfConstant= ["idAttrIfConstant"]
attrSliceIfConstant = ["attrSliceIfConstant"] 
outputIfConstant = ['idTypeIfConstant, idAttrIfConstant, idValueIfConstant'] 

### Then attribute is certain constant in the filtered global knowledge base
opThenConstant = """
    walk(resourceDict[addressThenConstant][1]["values"], [pathThenConstant, valueThenConstant])
    attrThenConstant := [elem | elem := pathThenConstant[n]; is_string(elem)]
    idAttrThenConstant := concat(".", attrThenConstant)
    any([resourceDetail[idTypeThenConstant][idAttrThenConstant] == "required", idAttrThenConstant in resourceDefaultView[idTypeThenConstant], idAttrThenConstant in resourceImportanceView[idTypeThenConstant]])
    idAttrThenConstant != "location"
    not contains(idAttrThenConstant, "size")
    not contains(idAttrThenConstant, "offer")
    not contains(idAttrThenConstant, "publisher")
    not contains(idAttrThenConstant, "product")
    not contains(idAttrThenConstant, "zone")
    attrSliceThenConstant := array.slice(attrThenConstant, 0, count(attrThenConstant)-1)
    count(resourceView[idTypeThenConstant][idAttrThenConstant]) > 1
    count(resourceView[idTypeThenConstant][idAttrThenConstant]) <= 8
    valueThenConstant == resourceView[idTypeThenConstant][idAttrThenConstant][_]
    not is_null(valueThenConstant)
    not contains(idAttrThenConstant, "tags")
    not contains(idAttrThenConstant, "id")
    not contains(idAttrThenConstant, "_name")
    idValueThenConstant := sprintf("%v", [valueThenConstant])
"""
pathThenConstant = ["pathThenConstant"]
idTypeThenConstant = ["idTypeThenConstant"]
addressThenConstant = ["addressThenConstant"]
idAttrThenConstant= ["idAttrThenConstant"]
attrSliceThenConstant = ["attrSliceThenConstant"] 
outputThenConstant = ['idTypeThenConstant, idAttrThenConstant, idValueThenConstant']

### If attribute1 is equal to attribute2, attributes are strings or booleans or numbers
opIfEqual = """
    walk(resourceDict[addressIfEqual1][1]["values"], [pathIfEqual1, valueIfEqual1])
    walk(resourceDict[addressIfEqual2][1]["values"], [pathIfEqual2, valueIfEqual2])
    any([is_string(valueIfEqual1), is_number(valueIfEqual1)])
    any([is_string(valueIfEqual2), is_number(valueIfEqual2)])
    #not net.cidr_contains("0.0.0.0/0", valueIfEqual1)
    #not net.cidr_contains("0.0.0.0/0", valueIfEqual2)
    valueIfEqual1 == valueIfEqual2
    not contains(valueIfEqual1, "*")
    not contains(valueIfEqual2, "*")
    any([pathIfEqual1 != pathIfEqual2, addressIfEqual1 != addressIfEqual2])
    attrIfEqual1 := [elem | elem := pathIfEqual1[n1]; is_string(elem)]
    attrIfEqual2 := [elem | elem := pathIfEqual2[n2]; is_string(elem)]
    idAttrIfEqual1 := concat(".", attrIfEqual1)
    idAttrIfEqual2 := concat(".", attrIfEqual2)
    any([resourceDetail[idTypeIfEqual1][idAttrIfEqual1] == "required", idAttrIfEqual1 in resourceDefaultView[idTypeIfEqual1], idAttrIfEqual1 in resourceImportanceView[idTypeIfEqual1]])
    any([resourceDetail[idTypeIfEqual2][idAttrIfEqual2] == "required", idAttrIfEqual2 in resourceDefaultView[idTypeIfEqual2], idAttrIfEqual2 in resourceImportanceView[idTypeIfEqual2]])
    #any([count(resourceView[idTypeIfEqual1][idAttrIfEqual1]) > 1, is_number(valueIfEqual1)])
    #any([count(resourceView[idTypeIfEqual2][idAttrIfEqual2]) > 1, is_number(valueIfEqual2)])
    attrSliceIfEqual1 := array.slice(attrIfEqual1, 0, count(attrIfEqual1)-1)
    attrSliceIfEqual2 := array.slice(attrIfEqual2, 0, count(attrIfEqual2)-1)
    #idAttrIfEqual1 <= idAttrIfEqual2
    not idAttrIfEqual1 in resourceReferenceView[idTypeIfEqual1]
    not idAttrIfEqual2 in resourceReferenceView[idTypeIfEqual2]
    not contains(idAttrIfEqual1, "tags")
    not contains(idAttrIfEqual1, "id")
    not contains(idAttrIfEqual2, "tags")
    not contains(idAttrIfEqual2, "id")
"""
pathIfEqual = ["pathIfEqual2"]
idTypeIfEqual = ["idTypeIfEqual1", "idTypeIfEqual2"]
addressIfEqual = ["addressIfEqual1", "addressIfEqual2"]
idAttrIfEqual= ["idAttrIfEqual1", "idAttrIfEqual2"]
attrSliceIfEqual = ["attrSliceIfEqual1", "attrSliceIfEqual2"] 
outputIfEqual = ['idTypeIfEqual1, idAttrIfEqual1, "String", "####", idTypeIfEqual2, idAttrIfEqual2, "String"']

### Then attribute1 is equal to attribute2, attributes are strings or booleans or numbers
opThenEqual = """
    walk(resourceDict[addressThenEqual1][1]["values"], [pathThenEqual1, valueThenEqual1])
    walk(resourceDict[addressThenEqual2][1]["values"], [pathThenEqual2, valueThenEqual2])
    any([is_string(valueThenEqual1), is_number(valueThenEqual1)])
    any([is_string(valueThenEqual2), is_number(valueThenEqual2)])
    #not net.cidr_contains("0.0.0.0/0", valueThenEqual1)
    #not net.cidr_contains("0.0.0.0/0", valueThenEqual2)
    valueThenEqual1 == valueThenEqual2
    not contains(valueThenEqual1, "*")
    not contains(valueThenEqual2, "*")
    #pathThenEqual1 != pathThenEqual2
    any([pathThenEqual1 != pathThenEqual2, addressThenEqual1 != addressThenEqual2])
    attrThenEqual1 := [elem | elem := pathThenEqual1[n1]; is_string(elem)]
    attrThenEqual2 := [elem | elem := pathThenEqual2[n2]; is_string(elem)]
    idAttrThenEqual1 := concat(".", attrThenEqual1)
    idAttrThenEqual2 := concat(".", attrThenEqual2)
    any([resourceDetail[idTypeThenEqual1][idAttrThenEqual1] == "required", idAttrThenEqual1 in resourceDefaultView[idTypeThenEqual1], idAttrThenEqual1 in resourceImportanceView[idTypeThenEqual1]])
    any([resourceDetail[idTypeThenEqual2][idAttrThenEqual2] == "required", idAttrThenEqual2 in resourceDefaultView[idTypeThenEqual2], idAttrThenEqual2 in resourceImportanceView[idTypeThenEqual2]])
    #any([count(resourceView[idTypeThenEqual1][idAttrThenEqual1]) > 1, is_number(valueThenEqual1)])
    #any([count(resourceView[idTypeThenEqual2][idAttrThenEqual2]) > 1, is_number(valueThenEqual2)])
    attrSliceThenEqual1 := array.slice(attrThenEqual1, 0, count(attrThenEqual1)-1)
    attrSliceThenEqual2 := array.slice(attrThenEqual2, 0, count(attrThenEqual2)-1)
    #idAttrThenEqual1 <= idAttrThenEqual2
    not idAttrThenEqual1 in resourceReferenceView[idTypeThenEqual1]
    not idAttrThenEqual2 in resourceReferenceView[idTypeThenEqual2]
    not contains(idAttrThenEqual1, "tags")
    not contains(idAttrThenEqual1, "id")
    not contains(idAttrThenEqual2, "tags")
    not contains(idAttrThenEqual2, "id")
"""
pathThenEqual = ["pathThenEqual2"]
idTypeThenEqual = ["idTypeThenEqual1", "idTypeThenEqual2"]
addressThenEqual = ["addressThenEqual1", "addressThenEqual2"]
idAttrThenEqual= ["idAttrThenEqual1", "idAttrThenEqual2"]
attrSliceThenEqual = ["attrSliceThenEqual1", "attrSliceThenEqual2"] 
outputThenEqual = ['idTypeThenEqual1, idAttrThenEqual1, "String", "####", idTypeThenEqual2, idAttrThenEqual2, "String"']

### If attribute1 is unequal to attribute2, attributes are strings or booleans or numbers
opIfUnequal = """
    walk(resourceDict[addressIfUnequal1][1]["values"], [pathIfUnequal1, valueIfUnequal1])
    walk(resourceDict[addressIfUnequal2][1]["values"], [pathIfUnequal2, valueIfUnequal2])
    any([is_string(valueIfUnequal1), is_number(valueIfUnequal1)])
    any([is_string(valueIfUnequal2), is_number(valueIfUnequal2)])
    valueIfUnequal1 != valueIfUnequal2
    not contains(valueIfUnequal1, "*")
    not contains(valueIfUnequal2, "*")
    #pathIfUnequal1 != pathIfUnequal2
    any([pathIfUnequal1 != pathIfUnequal2, addressIfUnequal1 != addressIfUnequal2])
    attrIfUnequal1 := [elem | elem := pathIfUnequal1[n1]; is_string(elem)]
    attrIfUnequal2 := [elem | elem := pathIfUnequal2[n2]; is_string(elem)]
    idAttrIfUnequal1 := concat(".", attrIfUnequal1)
    idAttrIfUnequal2 := concat(".", attrIfUnequal2)
    any([resourceDetail[idTypeIfUnequal1][idAttrIfUnequal1] == "required", idAttrIfUnequal1 in resourceDefaultView[idTypeIfUnequal1], idAttrIfUnequal1 in resourceImportanceView[idTypeIfUnequal1]])
    #any([count(resourceView[idTypeIfUnequal1][idAttrIfUnequal1]) > 1, is_number(valueIfUnequal1)])
    #any([resourceDetail[idTypeIfUnequal2][idAttrIfUnequal2] == "required", idAttrIfUnequal2 in resourceDefaultView[idTypeIfUnequal2]])
    idAttrIfUnequal1 == idAttrIfUnequal2
    not idAttrIfUnequal1 in resourceReferenceView[idTypeIfUnequal1]
    not contains(idAttrIfUnequal1, "tags")
    not contains(idAttrIfUnequal1, "id")
    not contains(idAttrIfUnequal1, "_name")
    not contains(idAttrIfUnequal2, "tags")
    not contains(idAttrIfUnequal2, "id")
    not contains(idAttrIfUnequal2, "_name")
"""
pathIfUnequal = ["pathIfUnequal2"]
idTypeIfUnequal = ["idTypeIfUnequal1", "idTypeIfUnequal2"]
addressIfUnequal = ["addressIfUnequal1", "addressIfUnequal2"]
idAttrIfUnequal= ["idAttrIfUnequal1", "idAttrIfUnequal2"]
attrSliceIfUnequal = [] 
outputIfUnequal = ['idTypeIfUnequal1, idAttrIfUnequal1, "String", "####", idTypeIfUnequal2, idAttrIfUnequal2, "String"']

### Then attribute1 is unequal to attribute2, attributes are strings or booleans or numbers
opThenUnequal = """
    walk(resourceDict[addressThenUnequal1][1]["values"], [pathThenUnequal1, valueThenUnequal1])
    walk(resourceDict[addressThenUnequal2][1]["values"], [pathThenUnequal2, valueThenUnequal2])
    any([is_string(valueThenUnequal1), is_number(valueThenUnequal1)])
    any([is_string(valueThenUnequal2), is_number(valueThenUnequal2)])
    #not net.cidr_contains("0.0.0.0/0", valueThenUnequal1)
    #not net.cidr_contains("0.0.0.0/0", valueThenUnequal2)
    valueThenUnequal1 != valueThenUnequal2
    not contains(valueThenUnequal1, "*")
    not contains(valueThenUnequal2, "*")
    #pathThenUnequal1 != pathThenUnequal2
    any([pathThenUnequal1 != pathThenUnequal2, addressThenUnequal1 != addressThenUnequal2])
    attrThenUnequal1 := [elem | elem := pathThenUnequal1[n1]; is_string(elem)]
    attrThenUnequal2 := [elem | elem := pathThenUnequal2[n2]; is_string(elem)]
    idAttrThenUnequal1 := concat(".", attrThenUnequal1)
    idAttrThenUnequal2 := concat(".", attrThenUnequal2)
    any([resourceDetail[idTypeThenUnequal1][idAttrThenUnequal1] == "required", idAttrThenUnequal1 in resourceDefaultView[idTypeThenUnequal1], idAttrThenUnequal1 in resourceImportanceView[idTypeThenUnequal1]])
    #any([count(resourceView[idTypeThenUnequal1][idAttrThenUnequal1]) > 1, is_number(valueThenUnequal1)])
    any([resourceDetail[idTypeThenUnequal2][idAttrThenUnequal2] == "required", idAttrThenUnequal2 in resourceDefaultView[idTypeThenUnequal2], idAttrThenUnequal2 in resourceImportanceView[idTypeThenUnequal2]])
    #attrThenUnequal1[count(attrThenUnequal1)-1] == attrThenUnequal2[count(attrThenUnequal2)-1]
    #any([idAttrThenUnequal1 == idAttrThenUnequal2, contains(idAttrThenUnequal1, idAttrThenUnequal2), contains(idAttrThenUnequal2, idAttrThenUnequal1)])
    idAttrThenUnequal1 == idAttrThenUnequal2
    not idAttrThenUnequal1 in resourceReferenceView[idTypeThenUnequal1]
    not contains(idAttrThenUnequal1, "tags")
    not contains(idAttrThenUnequal1, "id")
    not contains(idAttrThenUnequal1, "_name")
    not contains(idAttrThenUnequal2, "tags")
    not contains(idAttrThenUnequal2, "id")
    not contains(idAttrThenUnequal2, "_name")
"""
pathThenUnequal = ["pathThenUnequal2"]
idTypeThenUnequal = ["idTypeThenUnequal1", "idTypeThenUnequal2"]
addressThenUnequal = ["addressThenUnequal1", "addressThenUnequal2"]
idAttrThenUnequal= ["idAttrThenUnequal1", "idAttrThenUnequal2"]
attrSliceThenUnequal = [] 
outputThenUnequal = ['idTypeThenUnequal1, idAttrThenUnequal1, "String", "####", idTypeThenUnequal2, idAttrThenUnequal2, "String"']

### If attribute1 is contained within attribute2, attributes are CIDR ranges
opIfCIDRInclude = """
    walk(resourceDict[addressIfCIDRInclude1][1]["values"], [pathIfCIDRInclude1, valueIfCIDRInclude1])
    walk(resourceDict[addressIfCIDRInclude2][1]["values"], [pathIfCIDRInclude2, valueIfCIDRInclude2])
    #any([is_string(valueIfCIDRInclude1), is_boolean(valueIfCIDRInclude1), is_number(valueIfCIDRInclude1)])
    #any([is_string(valueIfCIDRInclude2), is_boolean(valueIfCIDRInclude2), is_number(valueIfCIDRInclude2)])
    net.cidr_is_valid(valueIfCIDRInclude1)
    net.cidr_is_valid(valueIfCIDRInclude2)
    valueIfCIDRInclude1 != "*"
    valueIfCIDRInclude2 != "*"
    net.cidr_contains(valueIfCIDRInclude2, valueIfCIDRInclude1)
    #pathIfCIDRInclude1 != pathIfCIDRInclude2
    any([pathIfCIDRInclude1 != pathIfCIDRInclude2, addressIfCIDRInclude1 != addressIfCIDRInclude2])
    attrIfCIDRInclude1 := [elem | elem := pathIfCIDRInclude1[n1]; is_string(elem)]
    attrIfCIDRInclude2 := [elem | elem := pathIfCIDRInclude2[n2]; is_string(elem)]
    idAttrIfCIDRInclude1 := concat(".", attrIfCIDRInclude1)
    idAttrIfCIDRInclude2 := concat(".", attrIfCIDRInclude2)
    idAttrIfCIDRInclude1 <= idAttrIfCIDRInclude2
    any([resourceDetail[idTypeIfCIDRInclude1][idAttrIfCIDRInclude1] == "required", idAttrIfCIDRInclude1 in resourceDefaultView[idTypeIfCIDRInclude1], idAttrIfCIDRInclude1 in resourceImportanceView[idTypeIfCIDRInclude1]])
    any([resourceDetail[idTypeIfCIDRInclude2][idAttrIfCIDRInclude2] == "required", idAttrIfCIDRInclude2 in resourceDefaultView[idTypeIfCIDRInclude2], idAttrIfCIDRInclude2 in resourceImportanceView[idTypeIfCIDRInclude2]])
    contains(idAttrIfCIDRInclude1, "address")
    contains(idAttrIfCIDRInclude2, "address")
    not contains(idAttrIfCIDRInclude1, "tags")
    not contains(idAttrIfCIDRInclude1, "id")
    not contains(idAttrIfCIDRInclude2, "tags")
    not contains(idAttrIfCIDRInclude2, "id")
"""
pathIfCIDRInclude = ["pathIfCIDRInclude2"]
idTypeIfCIDRInclude = ["idTypeIfCIDRInclude1", "idTypeIfCIDRInclude2"]
addressIfCIDRInclude = ["addressIfCIDRInclude1", "addressIfCIDRInclude2"]
idAttrIfCIDRInclude= ["idAttrIfCIDRInclude1", "idAttrIfCIDRInclude2"]
attrSliceIfCIDRInclude = [] 
outputIfCIDRInclude = ['idTypeIfCIDRInclude1, idAttrIfCIDRInclude1, "CIDR", "####", idTypeIfCIDRInclude2, idAttrIfCIDRInclude2, "CIDR"']

### Then attribute1 is contained within attribute2, attributes are CIDR ranges
opThenCIDRInclude = """
    walk(resourceDict[addressThenCIDRInclude1][1]["values"], [pathThenCIDRInclude1, valueThenCIDRInclude1])
    walk(resourceDict[addressThenCIDRInclude2][1]["values"], [pathThenCIDRInclude2, valueThenCIDRInclude2])
    #any([is_string(valueThenCIDRInclude1), is_boolean(valueThenCIDRInclude1), is_number(valueThenCIDRInclude1)])
    #any([is_string(valueThenCIDRInclude2), is_boolean(valueThenCIDRInclude2), is_number(valueThenCIDRInclude2)])
    net.cidr_is_valid(valueThenCIDRInclude1)
    net.cidr_is_valid(valueThenCIDRInclude2)
    valueThenCIDRInclude1 != "*"
    valueThenCIDRInclude2 != "*"
    net.cidr_contains(valueThenCIDRInclude2, valueThenCIDRInclude1)
    #pathThenCIDRInclude1 != pathThenCIDRInclude2
    any([pathThenCIDRInclude1 != pathThenCIDRInclude2, addressThenCIDRInclude1 != addressThenCIDRInclude2])
    attrThenCIDRInclude1 := [elem | elem := pathThenCIDRInclude1[n1]; is_string(elem)]
    attrThenCIDRInclude2 := [elem | elem := pathThenCIDRInclude2[n2]; is_string(elem)]
    idAttrThenCIDRInclude1 := concat(".", attrThenCIDRInclude1)
    idAttrThenCIDRInclude2 := concat(".", attrThenCIDRInclude2)
    idAttrThenCIDRInclude1 <= idAttrThenCIDRInclude2
    any([resourceDetail[idTypeThenCIDRInclude1][idAttrThenCIDRInclude1] == "required", idAttrThenCIDRInclude1 in resourceDefaultView[idTypeThenCIDRInclude1], idAttrThenCIDRInclude1 in resourceImportanceView[idTypeThenCIDRInclude1]])
    any([resourceDetail[idTypeThenCIDRInclude2][idAttrThenCIDRInclude2] == "required", idAttrThenCIDRInclude2 in resourceDefaultView[idTypeThenCIDRInclude2], idAttrThenCIDRInclude2 in resourceImportanceView[idTypeThenCIDRInclude2]])
    contains(idAttrThenCIDRInclude1, "address")
    contains(idAttrThenCIDRInclude2, "address")
    not contains(idAttrThenCIDRInclude1, "tags")
    not contains(idAttrThenCIDRInclude1, "id")
    not contains(idAttrThenCIDRInclude2, "tags")
    not contains(idAttrThenCIDRInclude2, "id")
"""
pathThenCIDRInclude = ["pathThenCIDRInclude2"]
idTypeThenCIDRInclude = ["idTypeThenCIDRInclude1", "idTypeThenCIDRInclude2"]
addressThenCIDRInclude = ["addressThenCIDRInclude1", "addressThenCIDRInclude2"]
idAttrThenCIDRInclude= ["idAttrThenCIDRInclude1", "idAttrThenCIDRInclude2"]
attrSliceThenCIDRInclude = [] 
outputThenCIDRInclude = ['idTypeThenCIDRInclude1, idAttrThenCIDRInclude1, "CIDR", "####", idTypeThenCIDRInclude2, idAttrThenCIDRInclude2, "CIDR"']

### If attribute1 does not overlap with attribute2, attributes are CIDR ranges
opIfCIDRExclude = """
    walk(resourceDict[addressIfCIDRExclude1][1]["values"], [pathIfCIDRExclude1, valueIfCIDRExclude1])
    walk(resourceDict[addressIfCIDRExclude2][1]["values"], [pathIfCIDRExclude2, valueIfCIDRExclude2])
    #any([is_string(valueIfCIDRExclude1), is_boolean(valueIfCIDRExclude1), is_number(valueIfCIDRExclude1)])
    #any([is_string(valueIfCIDRExclude2), is_boolean(valueIfCIDRExclude2), is_number(valueIfCIDRExclude2)])
    net.cidr_is_valid(valueIfCIDRExclude1)
    net.cidr_is_valid(valueIfCIDRExclude2)
    valueIfCIDRExclude1 != "*"
    valueIfCIDRExclude2 != "*"
    not net.cidr_intersects(valueIfCIDRExclude1, valueIfCIDRExclude2)
    #pathIfCIDRExclude1 != pathIfCIDRExclude2
    any([pathIfCIDRExclude1 != pathIfCIDRExclude2, addressIfCIDRExclude1 != addressIfCIDRExclude2])
    attrIfCIDRExclude1 := [elem | elem := pathIfCIDRExclude1[n1]; is_string(elem)]
    attrIfCIDRExclude2 := [elem | elem := pathIfCIDRExclude2[n2]; is_string(elem)]
    idAttrIfCIDRExclude1 := concat(".", attrIfCIDRExclude1)
    idAttrIfCIDRExclude2 := concat(".", attrIfCIDRExclude2)
    idAttrIfCIDRExclude1 <= idAttrIfCIDRExclude2
    any([resourceDetail[idTypeIfCIDRExclude1][idAttrIfCIDRExclude1] == "required", idAttrIfCIDRExclude1 in resourceDefaultView[idTypeIfCIDRExclude1], idAttrIfCIDRExclude1 in resourceImportanceView[idTypeIfCIDRExclude1]])
    any([resourceDetail[idTypeIfCIDRExclude2][idAttrIfCIDRExclude2] == "required", idAttrIfCIDRExclude2 in resourceDefaultView[idTypeIfCIDRExclude2], idAttrIfCIDRExclude2 in resourceImportanceView[idTypeIfCIDRExclude2]])
    contains(idAttrIfCIDRExclude1, "address")
    contains(idAttrIfCIDRExclude2, "address")
    not contains(idAttrIfCIDRExclude1, "tags")
    not contains(idAttrIfCIDRExclude1, "id")
    not contains(idAttrIfCIDRExclude2, "tags")
    not contains(idAttrIfCIDRExclude2, "id")
"""
pathIfCIDRExclude = ["pathIfCIDRExclude2"]
idTypeIfCIDRExclude = ["idTypeIfCIDRExclude1", "idTypeIfCIDRExclude2"]
addressIfCIDRExclude = ["addressIfCIDRExclude1", "addressIfCIDRExclude2"]
idAttrIfCIDRExclude= ["idAttrIfCIDRExclude1", "idAttrIfCIDRExclude2"]
attrSliceIfCIDRExclude = [] 
outputIfCIDRExclude = ['idTypeIfCIDRExclude1, idAttrIfCIDRExclude1, "CIDR", "####", idTypeIfCIDRExclude2, idAttrIfCIDRExclude2, "CIDR"']

### Then attribute1 does not overlap with attribute2, attributes are CIDR ranges
opThenCIDRExclude = """
    walk(resourceDict[addressThenCIDRExclude1][1]["values"], [pathThenCIDRExclude1, valueThenCIDRExclude1])
    walk(resourceDict[addressThenCIDRExclude2][1]["values"], [pathThenCIDRExclude2, valueThenCIDRExclude2])
    #any([is_string(valueThenCIDRExclude1), is_boolean(valueThenCIDRExclude1), is_number(valueThenCIDRExclude1)])
    #any([is_string(valueThenCIDRExclude2), is_boolean(valueThenCIDRExclude2), is_number(valueThenCIDRExclude2)])
    net.cidr_is_valid(valueThenCIDRExclude1)
    net.cidr_is_valid(valueThenCIDRExclude2)
    valueThenCIDRExclude1 != "*"
    valueThenCIDRExclude2 != "*"
    not net.cidr_intersects(valueThenCIDRExclude1, valueThenCIDRExclude2)
    #pathThenCIDRExclude1 != pathThenCIDRExclude2
    any([pathThenCIDRExclude1 != pathThenCIDRExclude2, addressThenCIDRExclude1 != addressThenCIDRExclude2])
    attrThenCIDRExclude1 := [elem | elem := pathThenCIDRExclude1[n1]; is_string(elem)]
    attrThenCIDRExclude2 := [elem | elem := pathThenCIDRExclude2[n2]; is_string(elem)]
    idAttrThenCIDRExclude1 := concat(".", attrThenCIDRExclude1)
    idAttrThenCIDRExclude2 := concat(".", attrThenCIDRExclude2)
    #idAttrThenCIDRExclude1 <= idAttrThenCIDRExclude2
    any([resourceDetail[idTypeThenCIDRExclude1][idAttrThenCIDRExclude1] == "required", idAttrThenCIDRExclude1 in resourceDefaultView[idTypeThenCIDRExclude1], idAttrThenCIDRExclude1 in resourceImportanceView[idTypeThenCIDRExclude1]])
    any([resourceDetail[idTypeThenCIDRExclude2][idAttrThenCIDRExclude2] == "required", idAttrThenCIDRExclude2 in resourceDefaultView[idTypeThenCIDRExclude2], idAttrThenCIDRExclude2 in resourceImportanceView[idTypeThenCIDRExclude2]])
    contains(idAttrThenCIDRExclude1, "address")
    contains(idAttrThenCIDRExclude2, "address")
    not contains(idAttrThenCIDRExclude1, "tags")
    not contains(idAttrThenCIDRExclude1, "id")
    not contains(idAttrThenCIDRExclude2, "tags")
    not contains(idAttrThenCIDRExclude2, "id")
"""
pathThenCIDRExclude = ["pathThenCIDRExclude2"]
idTypeThenCIDRExclude = ["idTypeThenCIDRExclude1", "idTypeThenCIDRExclude2"]
addressThenCIDRExclude = ["addressThenCIDRExclude1", "addressThenCIDRExclude2"]
idAttrThenCIDRExclude= ["idAttrThenCIDRExclude1", "idAttrThenCIDRExclude2"]
attrSliceThenCIDRExclude = [] 
outputThenCIDRExclude = ['idTypeThenCIDRExclude1, idAttrThenCIDRExclude1, "CIDR", "####", idTypeThenCIDRExclude2, idAttrThenCIDRExclude2, "CIDR"']

### If some attribute is of enum type, not e.g. random strings
opIfEnum= """
    walk(resourceDict[addressIfEnum][1]["values"], [pathIfEnum, valueIfEnum])
    is_string(pathIfEnum[count(pathIfEnum)-1]) 
    attrIfEnum := [elem | elem := pathIfEnum[n]; is_string(elem)]
    idAttrIfEnum := concat(".", attrIfEnum)
    count(resourceView[idTypeIfEnum][idAttrIfEnum]) > 1
    count(attrIfEnum) <= 2
    idAttrIfEnum in resourceImportanceView[idTypeIfEnum]
    attrSliceIfEnum := array.slice(attrIfEnum, 0, count(attrIfEnum)-1)
    any([is_string(valueIfEnum), is_boolean(valueIfEnum)])
    not contains(idAttrIfEnum, "location")
    not contains(idAttrIfEnum, "tags")
    not contains(idAttrIfEnum, "id")
    not contains(idAttrIfEnum, "_name")
"""
pathIfEnum = ["pathIfEnum"]
idTypeIfEnum = ["idTypeIfEnum"]
addressIfEnum = ["addressIfEnum"]
idAttrIfEnum= ["idAttrIfEnum"]
attrSliceIfEnum = []
outputIfEnum = ['idTypeIfEnum, idAttrIfEnum, "Enum"'] 

### Then some attribute is of enum type, not e.g. random strings
opThenEnum= """
    walk(resourceDict[addressThenEnum][1]["values"], [pathThenEnum, valueThenEnum])
    is_string(pathThenEnum[count(pathThenEnum)-1]) 
    attrThenEnum := [elem | elem := pathThenEnum[n]; is_string(elem)]
    idAttrThenEnum := concat(".", attrThenEnum)
    count(resourceView[idTypeThenEnum][idAttrThenEnum]) > 1
    idAttrThenEnum in resourceImportanceView[idTypeThenEnum]
    attrSliceThenEnum := array.slice(attrThenEnum, 0, count(attrThenEnum)-1)
    any([is_string(valueThenEnum), is_boolean(valueThenEnum)])
    #any([contains(idAttrThenEnum, "type"), contains(idAttrThenEnum, "name"), contains(idAttrThenEnum, "priority"), contains(idAttrThenEnum, "enable")])
    not contains(idAttrThenEnum, "location")
    not contains(idAttrThenEnum, "tags")
    not contains(idAttrThenEnum, "id")
    not contains(idAttrThenEnum, "_name")
"""
pathThenEnum = ["pathThenEnum"]
idTypeThenEnum = ["idTypeThenEnum"]
addressThenEnum = ["addressThenEnum"]
idAttrThenEnum= ["idAttrThenEnum"]
attrSliceThenEnum = []
outputThenEnum = ['idTypeThenEnum, idAttrThenEnum, "Enum"']

### If some attribute is of CIDR type, with unknown mask requiremts
opIfCIDRMask= """
    walk(resourceDict[addressIfCIDRMask][1]["values"], [pathIfCIDRMask, valueIfCIDRMask])
    any([is_string(valueIfCIDRMask), is_boolean(valueIfCIDRMask), is_number(valueIfCIDRMask)])
    net.cidr_is_valid(valueIfCIDRMask)
    cidrDetailIfCIDRMask := split(valueIfCIDRMask, "/")
    maskLengthIfCIDRMask := to_number(cidrDetailIfCIDRMask[1])
    maskLengthIfCIDRMask <= 26
    attrIfCIDRMask := [elem | elem := pathIfCIDRMask[n1]; is_string(elem)]
    idAttrIfCIDRMask := concat(".", attrIfCIDRMask)
    contains(idAttrIfCIDRMask, "address")
    not contains(idAttrIfCIDRMask, "tags")
    not contains(idAttrIfCIDRMask, "id")
"""
pathIfCIDRMask = ["pathIfCIDRMask"]
idTypeIfCIDRMask = ["idTypeIfCIDRMask"]
addressIfCIDRMask = ["addressIfCIDRMask"]
idAttrIfCIDRMask= ["idAttrIfCIDRMask"]
attrSliceIfCIDRMask = []
outputIfCIDRMask = ['idTypeIfCIDRMask, idAttrIfCIDRMask, "CIDR"'] 

### Then some attribute is of CIDR type, with unknown mask requiremts
opThenCIDRMask= """
    walk(resourceDict[addressThenCIDRMask][1]["values"], [pathThenCIDRMask, valueThenCIDRMask])
    any([is_string(valueThenCIDRMask), is_boolean(valueThenCIDRMask), is_number(valueThenCIDRMask)])
    net.cidr_is_valid(valueThenCIDRMask)
    cidrDetailThenCIDRMask := split(valueThenCIDRMask, "/")
    maskLengthThenCIDRMask := to_number(cidrDetailThenCIDRMask[1])
    maskLengthThenCIDRMask <= 26
    attrThenCIDRMask := [elem | elem := pathThenCIDRMask[n1]; is_string(elem)]
    idAttrThenCIDRMask := concat(".", attrThenCIDRMask)
    contains(idAttrThenCIDRMask, "address")
    not contains(idAttrThenCIDRMask, "tags")
    not contains(idAttrThenCIDRMask, "id")
"""
pathThenCIDRMask = ["pathThenCIDRMask"]
idTypeThenCIDRMask = ["idTypeThenCIDRMask"]
addressThenCIDRMask = ["addressThenCIDRMask"]
idAttrThenCIDRMask= ["idAttrThenCIDRMask"]
attrSliceThenCIDRMask = []
outputThenCIDRMask = ['idTypeThenCIDRMask, idAttrThenCIDRMask, "CIDR"'] 

### If attribute1 and attrbute2 are certain constants in the filtered global knowledge base
opIfBinConstant = """
    walk(resourceDict[addressIfBinConstant1][1]["values"], [pathIfBinConstant1, valueIfBinConstant1])
    walk(resourceDict[addressIfBinConstant2][1]["values"], [pathIfBinConstant2, valueIfBinConstant2])
    #pathIfBinConstant1 < pathIfBinConstant2
    attrIfBinConstant1 := [elem | elem := pathIfBinConstant1[n]; is_string(elem)]
    attrIfBinConstant2 := [elem | elem := pathIfBinConstant2[n]; is_string(elem)]
    idAttrIfBinConstant1 := concat(".", attrIfBinConstant1)
    idAttrIfBinConstant2 := concat(".", attrIfBinConstant2)
    idAttrIfBinConstant1 <= idAttrIfBinConstant2
    is_boolean(valueIfBinConstant1)
    is_boolean(valueIfBinConstant2)
    #valueIfBinConstant1 in resourceView[valueIfBinConstant1][idAttrIfBinConstant1]
    idAttrIfBinConstant1 in resourceDefaultView[idTypeIfBinConstant1]
    idAttrIfBinConstant2 in resourceDefaultView[idTypeIfBinConstant2]
    attrSliceIfBinConstant1 := array.slice(attrIfBinConstant1, 0, count(attrIfBinConstant1)-1)
    attrSliceIfBinConstant2 := array.slice(attrIfBinConstant2, 0, count(attrIfBinConstant2)-1)
    attrSliceIfBinConstant1 == attrSliceIfBinConstant2
    idValueIfBinConstant1 := sprintf("%v", [valueIfBinConstant1])
    idValueIfBinConstant2 := sprintf("%v", [valueIfBinConstant2])
"""
pathIfBinConstant = ["pathIfBinConstant1", "pathIfBinConstant2"]
idTypeIfBinConstant = ["idTypeIfBinConstant1", "idTypeIfBinConstant2"]
addressIfBinConstant = ["addressIfBinConstant1", "addressIfBinConstant2"]
idAttrIfBinConstant= ["idAttrIfBinConstant1", "idAttrIfBinConstant2"]
attrSliceIfBinConstant = ["attrSliceIfBinConstant1", "attrSliceIfBinConstant2"] 
outputIfBinConstant = ['idTypeIfBinConstant1, idAttrIfBinConstant1, idValueIfBinConstant1, "####", idTypeIfBinConstant2, idAttrIfBinConstant2, idValueIfBinConstant2']

### Then attribute1 and attrbute2 are certain constants in the filtered global knowledge base
opThenBinConstant = """
    walk(resourceDict[addressThenBinConstant1][1]["values"], [pathThenBinConstant1, valueThenBinConstant1])
    walk(resourceDict[addressThenBinConstant2][1]["values"], [pathThenBinConstant2, valueThenBinConstant2])
    #pathThenBinConstant1 <= pathThenBinConstant2
    attrThenBinConstant1 := [elem | elem := pathThenBinConstant1[n]; is_string(elem)]
    attrThenBinConstant2 := [elem | elem := pathThenBinConstant2[n]; is_string(elem)]
    idAttrThenBinConstant1 := concat(".", attrThenBinConstant1)
    idAttrThenBinConstant2 := concat(".", attrThenBinConstant2)
    idAttrThenBinConstant1 <= idAttrThenBinConstant2
    is_boolean(valueThenBinConstant1)
    is_boolean(valueThenBinConstant2)
    idAttrThenBinConstant1 in resourceDefaultView[idTypeThenBinConstant1]
    idAttrThenBinConstant2 in resourceDefaultView[idTypeThenBinConstant2]
    attrSliceThenBinConstant1 := array.slice(attrThenBinConstant1, 0, count(attrThenBinConstant1)-1)
    attrSliceThenBinConstant2 := array.slice(attrThenBinConstant2, 0, count(attrThenBinConstant2)-1)
    attrSliceThenBinConstant1 == attrSliceThenBinConstant2
    idValueThenBinConstant1 := sprintf("%v", [valueThenBinConstant1])
    idValueThenBinConstant2 := sprintf("%v", [valueThenBinConstant2])
"""
pathThenBinConstant = ["pathThenBinConstant1", "pathThenBinConstant2"]
idTypeThenBinConstant = ["idTypeThenBinConstant1", "idTypeThenBinConstant2"]
addressThenBinConstant = ["addressThenBinConstant1", "addressThenBinConstant2"]
idAttrThenBinConstant= ["idAttrThenBinConstant1", "idAttrThenBinConstant2"]
attrSliceThenBinConstant = ["attrSliceThenBinConstant1", "attrSliceThenBinConstant2"]
outputThenBinConstant = ['idTypeThenBinConstant1, idAttrThenBinConstant1, idValueThenBinConstant1, "####", idTypeThenBinConstant2, idAttrThenBinConstant2, idValueThenBinConstant2']

### rule extraction mechansim for mining, targeting attribute relation-only rules
def constructRegoAttr(resourceType, opType):
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
    with open(f"../schemaFiles/{providerType}KBSchemaCompleteView.json", "r") as f:
        resourceCompleteViewString = f.read()
    
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
    fuzzyList = ["CountChild", "CountParent", "Enum", "CIDRMask"]
    
    opCombinations = []
    regoOpString = ""
    for index1 in range(len(opIfList)):
        for index2 in range(index1, len(opThenList)):
            item1 = opIfList[index1]
            item2 = opThenList[index2]
            opName1, opName2 = item1[0], item2[0]
            
            if (opName1 in fuzzyList and opName2 not in fuzzyList) or  (opName1 not in fuzzyList and opName2 in fuzzyList):
                continue
            if opName1 in ["Constant"] and opName2 in ["Equal", "Unequal", "CIDRInclude", "CIDRExclude"]:
                continue
            if opName1 == "Absence" and opName2 == "Absence":
                continue
            idTypeList1, idTypeList2 = item1[2], item2[2]
            addressList1, addressList2 = item1[3], item2[3]
            pathList1, pathList2 = item1[4], item2[4]
            idAttrList1, idAttrList2 = item1[5], item2[5]
            attrSliceList1, attrSliceList2 = item1[6], item2[6]
            output1, output2 = item1[7][0], item2[7][0]
            regoOpString += f"Attr{opName1}Then{opName2}List := [rule |\n" 
            
            for ele1 in range(len(addressList1)):
                idType1 = idTypeList1[ele1]
                address1 = addressList1[ele1]
                regoOpString += f'    {idType1} := resourceDict[{address1}][0]["type"]\n'
                regoOpString += f'    {idType1} == "{resourceType}"\n'
            for ele2 in range(len(addressList2)):
                idType2 = idTypeList2[ele2]
                address2 = addressList2[ele2]
                regoOpString += f'    {idType2} := resourceDict[{address2}][0]["type"]\n'
            
            addressList = addressList1 + addressList2
            for ele1 in range(len(addressList)-1):
                address1 = addressList[ele1]
                address2 = addressList[ele1+1]
                regoOpString += f"    {address1} == {address2}\n"
            regoOpString += item1[1]
            regoOpString += item2[1] + "\n"
            
            for path1 in pathList1:
                for path2 in pathList2:
                    regoOpString += f"    {path1} != {path2}\n"
            for idAttr1 in idAttrList1:
                for idAttr2 in idAttrList2:
                    if opName1 == "Enum" and opName2 == "Enum":
                        regoOpString += f"    {idAttr1} != {idAttr2}\n"
                    elif opName1 == opName2:
                        regoOpString += f"    {idAttr1} < {idAttr2}\n"
                    else:
                        regoOpString += f"    {idAttr1} != {idAttr2}\n"
            
            ### Handling equality attribute constraints
            if opName1 in ["Equal", "CIDRExclude", "CIDRInclude", "Unequal"]:
                idAttr1 = idAttrList1[0]
                idAttr2 = idAttrList1[1]
                regoOpString += f"    {idAttr1} == {idAttr2}\n"
                if opName2 not in  ["Equal", "CIDRExclude", "CIDRInclude", "Unequal"]:
                    idAttr3 = idAttrList2[0]
                    regoOpString += f"    contains({idAttr1},{idAttr3})\n"
            if opName2 in ["Equal", "CIDRExclude", "CIDRInclude", "Unequal"]:
                idAttr1 = idAttrList2[0]
                idAttr2 = idAttrList2[1]
                regoOpString += f"    {idAttr1} == {idAttr2}\n"
                if opName1 not in  ["Equal", "CIDRExclude", "CIDRInclude", "Unequal"]:
                    idAttr3 = idAttrList1[0]
                    regoOpString += f"    contains({idAttr1},{idAttr3})\n"
            if opName1 == "Enum" and opName2 == "Enum":
                regoOpString += f'    any([contains(idAttrThenEnum, "type"), contains(idAttrThenEnum, "name"), contains(idAttrThenEnum, "priority"), contains(idAttrThenEnum, "enable"), contains(idAttrThenEnum, "publisher"), contains(idAttrThenEnum, "offer"), contains(idAttrThenEnum, "version")])\n'
                regoOpString += f'    not any([contains(idAttrThenEnum, "name"), contains(idAttrThenEnum, "sku"), contains(idAttrThenEnum, "size")])\n'
                regoOpString += f'    not any([contains(idAttrIfEnum, "publisher"), contains(idAttrIfEnum, "offer"), contains(idAttrIfEnum, "version")])\n'
                #regoOpString += f'    not contains(idAttrIfEnum, "version")\n'
                regoOpString += f'    any([contains(idAttrIfEnum, "size") == false, contains(idAttrThenEnum, "reference") == false])\n'
                regoOpString += f'    any([count(attrSliceIfEnum) < count(attrSliceThenEnum), attrSliceIfEnum == attrSliceThenEnum])\n'
            ### This could filter out some good rules???
            for attrSlice1 in attrSliceList1:
                for attrSlice2 in attrSliceList2:
                    if (opName1 == "Existence" or opName1 == "Absence") and opName2 == "Constant":
                        idAttr1 = idAttrList1[0]
                        idAttr2 = idAttrList2[0]
                        regoOpString += f'    any([contains({idAttr2}, {idAttr1}), contains({idAttr2}, "sku")])\n'
                        regoOpString += f"    count({attrSlice1}) <= count({attrSlice2})\n"
                    elif opName1 == "Constant" and opName2 == "Constant":
                        regoOpString += f"    count({attrSlice1}) <= count({attrSlice2})\n"
                    else:
                        regoOpString += f"    {attrSlice1} == {attrSlice2}\n"
            regoOpString += f'    rule := concat(" ", ["{opName1}Then{opName2}", "####", '
            regoOpString += f'{output1}, "####", {output2}])\n'
            regoOpString += "]\n\n"
            opCombinations.append(f"Attr{opName1}Then{opName2}List")
    
    regoString = "resourceDetail := "+ resourceDetailString + "\n" + \
                 "resourceView := "+ resourceViewString + "\n" + \
                 "resourceDefaultView := "+ resourceDefaultViewString + "\n" + \
                 "resourceCompleteView := " + resourceCompleteViewString + "\n" + \
                 "resourceImportanceView := " + resourceImportanceViewString + "\n" + \
                 "resourceReferenceView := " + resourceReferenceViewString + "\n" + \
                 "resourceTrivialView := " + resourceTrivialViewString + "\n" +  regoOpString
    return regoString, opCombinations

