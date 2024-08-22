### Main entry to the knowledge base construction process. The two 
### required inputs are 1. Terraform Azurerm Schema file, and 2. Crawled
### programs in rego format. The constructed knowledge will be stored
### in schemaFiles.
import os
import sys
sys.path.insert(0, '..')
import utils.utils as utils
import json
from collections import defaultdict
import dataPreprocessing.getRegoFormat as getRegoFormat
import multiprocessing
import argparse

headerString = """
package assemble
import data.fugue.resource_view.resource_view_input
import future.keywords.in
"""

regoFileCommandString = """
resultString := [[type, idAttr, value] |
    address := configList[a]["resources"][id]["id"]
    type := configList[a]["resources"][id]["_type"]
    walk(configList[a]["resources"][id], [path, value])
    attr := [elem |
        elem := path[n]
        is_string(elem)
    ]
    not attr[0] in ["_filepath", "_provider", "_tags", "_type", "id", "name", "tags", "template", "depends_on"]
    is_string(value)
    idAttr := concat(".", attr)
]
resultBoolean := [[type, idAttr, value] |
    address := configList[a]["resources"][id]["id"]
    type := configList[a]["resources"][id]["_type"]
    walk(configList[a]["resources"][id], [path, value])
    attr := [elem |
        elem := path[n]
        is_string(elem)
    ]
    not attr[0] in ["_filepath", "_provider", "_tags", "_type", "id", "name", "tags", "template", "depends_on"]
    is_boolean(value)
    idAttr := concat(".", attr)
]
resultNull := [[type, idAttr, value] |
    address := configList[a]["resources"][id]["id"]
    type := configList[a]["resources"][id]["_type"]
    walk(configList[a]["resources"][id], [path, temp])
    attr := [elem |
        elem := path[n]
        is_string(elem)
    ]
    not attr[0] in ["_filepath", "_provider", "_tags", "_type", "id", "name", "tags", "template", "depends_on"]
    is_null(temp)
    value := "null"
    idAttr := concat(".", attr)
]
result1 := array.concat(resultString, resultBoolean)
result := array.concat(resultNull, result1)
""".format(bracket1 = "{", bracket2 = "}")

regoRepoCommandString = """
childPlannedModules :=  object.get(mock_config.planned_values.root_module, "child_modules", [])
rootPlan := object.get(mock_config.planned_values.root_module, "resources", [])
childPlan := [item |
    item := childPlannedModules[_].resources[_]
]
plan := array.concat(rootPlan, childPlan)

childConfigedModules := object.get(mock_config.configuration.root_module, "child_modules", [])
rootConfig := object.get(mock_config.configuration.root_module, "resources", [])
childConfig := [item |
   item := childConfigedModules[_].resources[_]
]
config := array.concat(rootConfig, childConfig)

resultConfigAttr[address] := attrList {bracket1}
    address := config[id]["address"]
    type := config[id]["type"]
    attrList := [idAttr |
        walk(config[id]["expressions"], [path, value])
        attr := [elem | 
            elem := path[n]
            is_string(elem)
            elem != "constant_value"
            elem != "references"
        ]
        idAttr := concat(".", attr)
        not any([idAttr == "name", idAttr == "id"])
        not any([contains(idAttr, "_name"), contains(idAttr, "_id")])
        any([is_string(value), is_boolean(value), is_number(value), is_array(value), is_object(value)])
    ]
{bracket2}

resultConfigTopo[address] := attrList {bracket1}
    address := config[id]["address"]
    type := config[id]["type"]
    attrList := [idAttr |
        walk(config[id]["expressions"], [path, value])
        "references" == path[count(path)-2]
        attr := [elemStr | 
            elem := path[n]
            n < count(path)-2
            elemStr := sprintf("%v", [elem])
        ]
        idAttr := concat(".", attr)
        any([idAttr == "name", idAttr == "id", contains(idAttr, "_name"), contains(idAttr, "_id")])
    ]
{bracket2}

resultConfig[address] := attrList {bracket1}
    address := config[id]["address"]
    attrList := {bracket1}idAttr | idAttr := resultConfigTopo[address][_]{bracket2} | {bracket1}idAttr | idAttr := resultConfigAttr[address][_]{bracket2}
{bracket2}

resultPlan[address] := attrList {bracket1}
    address := plan[id]["address"]
    type := plan[id]["type"]
    attrList := [idAttr |
        walk(plan[id]["values"], [path, value])
        attr := [elem | elem := path[n]; is_string(elem)]
        idAttr := concat(".", attr)
        any([is_string(value), is_boolean(value), is_number(value), is_array(value)])
        value != ""
        value != null
        value != []
    ]
{bracket2}

resultDefault[address] := attrList {bracket1}
    address := plan[id]["address"]
    attrList := [idAttr |
        idAttr := resultPlan[address][_]
        not idAttr in resultConfig[address]
    ]
{bracket2}

resultDependency := [[type1, type2, idAttr1, idAttr2] |
    walk(config[id1], [path1, value1])
    address1 := config[id1]["address"]
    address2 := config[id2]["address"]
    id1 != id2
    type1 := config[id1]["type"]
    type2 := config[id2]["type"]
    "references" == path1[count(path1)-2]
    address2 != value1
    idAddr2 := concat(".", [address2, ""])
    startswith(value1, idAddr2)
    attr1 := [elemStr |
        elem := path1[n]
        n > 0; n < count(path1)-2
        elemStr := sprintf("%v", [elem])
    ]
    idAttr1 := concat(".", attr1)
    idAttr2 := trim_prefix(value1, idAddr2)
    any([idAttr2 == "name", idAttr2 == "id"])
    any([contains(idAttr1, "_name"), contains(idAttr1, "_id")])
]

resultString := [[type, idAttr, value] |
    address := plan[id]["address"]
    type := plan[id]["type"]
    walk(plan[id]["values"], [path, value])
    attr := [elem |
        elem := path[n]
        is_string(elem)
    ]
    is_string(value)
    idAttr := concat(".", attr)
]
resultBoolean := [[type, idAttr, value] |
    address := plan[id]["address"]
    type := plan[id]["type"]
    walk(plan[id]["values"], [path, value])
    attr := [elem |
        elem := path[n]
        is_string(elem)
    ]
    is_boolean(value)
    #value := sprintf("%v", [temp])
    idAttr := concat(".", attr)
]
resultNumber := [[type, idAttr, value] |
    address := plan[id]["address"]
    type := plan[id]["type"]
    walk(plan[id]["values"], [path, value])
    attr := [elem |
        elem := path[n]
        is_string(elem)
    ]
    is_number(value)
    #value := sprintf("%v", [temp])
    idAttr := concat(".", attr)
]
resultNull := [[type, idAttr, value] |
    address := plan[id]["address"]
    type := plan[id]["type"]
    walk(plan[id]["values"], [path, temp])
    attr := [elem |
        elem := path[n]
        is_string(elem)
    ]
    is_null(temp)
    value := "NULL"
    idAttr := concat(".", attr)
]
result1 := array.concat(resultString, resultBoolean)
result2 := array.concat(resultNumber, result1)
result := array.concat(resultNull, result2)
""".format(bracket1 = "{", bracket2 = "}")

regoRegistryCommandString = """
plan := object.get(mock_config.planned_values.root_module, "resources", [])
config := object.get(mock_config.configuration.root_module, "resources", [])

dependencyList := [[type1, type2, idAttr1, idAttr2] |
    walk(config[id1], [path1, value1])
    address1 := config[id1]["address"]
    address2 := config[id2]["address"]
    type1 := config[id1]["type"]
    type2 := config[id2]["type"]
    id1 != id2
    "references" == path1[count(path1)-2]
    #address2 in value1
    address2 != value1
    idAddr2 := concat(".", [address2, ""])
    startswith(value1, idAddr2)
    attr1 := [elem |
        elem := path1[n]
        n > 0; n < count(path1)-2
        is_string(elem)
    ]
    idAttr1 := concat(".", attr1)
    idAttr2 := trim_prefix(value1, idAddr2)
]
result := dependencyList
""".format(bracket1 = "{", bracket2 = "}")

regoSchemaString = """
resources := mock_config["provider_schemas"]["registry.terraform.io/hashicorp/azurerm"]["resource_schemas"]
resultOptional := [[type, idAttr, "optional", "attribute"] |
    walk(resources[type], [path, value])
    path[count(path)-1] == "optional"
    attr := [elem |
        elem := path[n]
        is_string(elem)
        elem != "attributes"
        elem != "block"
        elem != "block_types"
        elem != "optional"
    ]
    idAttr := concat(".", attr)
]
resultRequired := [[type, idAttr, "required", "attribute"] |
    walk(resources[type], [path, value])
    path[count(path)-1] == "required"
    attr := [elem |
        elem := path[n]
        is_string(elem)
        elem != "attributes"
        elem != "block"
        elem != "block_types"
        elem != "required"
    ]
    idAttr := concat(".", attr)
]
resultNested := [[type, idAttr, "nested", minItems] |
    walk(resources[type], [path, value])
    nested := object.get(value, "nesting_mode", "")
    minItems := object.get(value, "min_items", 0)
    nested != ""
    attr := [elem |
        elem := path[n]
        is_string(elem)
        elem != "attributes"
        elem != "block"
        elem != "block_types"
        elem != "nesting_mode"
    ]
    idAttr := concat(".", attr)
]

resultSubset := [[type, idAttr, "required", "attribute"] |
    walk(resources[type], [path, value])
    #path[count(path)-1] == "type"
    #path[count(path)-3] == "attributes"
    attrName := path[count(path)-2]
    is_array(value)
    value[0] == "set"
    value[1][0] == "object"
    minItems := value[1][1]
    subAttrType := minItems[subAttrName]
    attr := [attrName, subAttrName]
    idAttr := concat(".", attr)
]

resultListTemp1 := array.concat(resultOptional, resultRequired)
resultListTemp2 := array.concat(resultListTemp1, resultNested)
resultList := array.concat(resultListTemp2, resultSubset)

result[type] := idAttrs {
    type := resultList[_][0]
    idAttrs := [idAttr |
        resultList[n][0] == type
        idAttr := resultList[n][1]
    ]
}  
resultDetail[type] := idAttrs {
    type := resultList[_][0]
    idAttrs := [[idAttr, reqORopt, attrSchemaType] |
        resultList[n][0] == type
        idAttr := resultList[n][1]
        reqORopt := resultList[n][2]
        attrSchemaType := resultList[n][3]
    ]
}

resultCompleteAttrList := [[type, idAttr, schemaType] |
    walk(resources[type], [path, value])
    path[count(path)-1] == "type"
    not is_object(value)
    not is_array(value)
    schemaType := value
    attr := [elem |
        elem := path[n]
        is_string(elem)
        elem != "attributes"
        elem != "block"
        elem != "block_types"
        elem != "nesting_mode"
        n < count(path)-1
    ]
    idAttr := concat(".", attr)
]

resultCompleteListList := [[type, idAttr, "list"] |
    walk(resources[type], [path, value])
    path[count(path)-1] == "type"
    not is_object(value)
    is_array(value)
    schemaType := value[0]
    attr := [elem |
        elem := path[n]
        is_string(elem)
        elem != "attributes"
        elem != "block"
        elem != "block_types"
        elem != "nesting_mode"
        n < count(path)-1
    ]
    idAttr := concat(".", attr)
]

resultCompleteBlockList := [[type, idAttr, "block"] |
    walk(resources[type], [path, value])
    path[count(path)-2] == "block_types"
    attr := [elem |
        elem := path[n]
        is_string(elem)
        elem != "attributes"
        elem != "block"
        elem != "block_types"
        elem != "nesting_mode"
    ]
    idAttr := concat(".", attr)
]
resultCompleteListTemp := array.concat(resultCompleteAttrList, resultCompleteBlockList)
resultCompleteList := array.concat(resultCompleteListTemp, resultCompleteListList)

resultComplete[type] := idAttrs {
    type := resultCompleteList[_][0]
    idAttrs := [[idAttr, schemaType] |
        resultCompleteList[n][0] == type
        idAttr := resultCompleteList[n][1]
        schemaType := resultCompleteList[n][2]
    ]
}
"""


regoGPTString = """
result1 := [typeList |
    mock_config_GPT[type][idAttr][n]
    n != "not_enum"
    enum_array := mock_config_GPT[type][idAttr][n]
    is_array(enum_array)
    typeList := array.concat([type, idAttr], enum_array)
]
result2 := [typeList |
    mock_config_GPT[type][idAttr][n]
    n != "not_enum"
    enum_array := mock_config_GPT[type][idAttr][n][idAttr]
    is_array(enum_array)
    typeList := array.concat([type, idAttr], enum_array)
]
result := array.concat(result1, result2)
"""

def call_regoMDCCount(filepath, count, outputpath):
    print(count, filepath)
    utils.execute_cmd_imm(f'timeout 40 opa eval -d {filepath} "data.assemble.result" > {outputpath}')

def call_regoDefaultValue(filepath, count, outputpath):
    print(count, filepath)
    utils.execute_cmd_imm(f'timeout 40 opa eval -d {filepath} "data.assemble.resultDefault" > {outputpath}')

def call_regoConfigValue(filepath, count, outputpath):
    print(count, filepath)
    utils.execute_cmd_imm(f'timeout 40 opa eval -d {filepath} "data.assemble.resultConfig" > {outputpath}')
    
def call_regoDependency(filepath, count, outputpath):
    print(count, filepath)
    utils.execute_cmd_imm(f'timeout 40 opa eval -d {filepath} "data.assemble.resultDependency" > {outputpath}')

def call_regoSchemaDetail(filepath, count, outputpath):
    print(count, filepath)
    utils.execute_cmd_imm(f'timeout 40 opa eval -d {filepath} "data.assemble.resultDetail" > {outputpath}')

def call_regoSchemaComplete(filepath, count, outputpath):
    print(count, filepath)
    utils.execute_cmd_imm(f'timeout 40 opa eval -d {filepath} "data.assemble.resultComplete" > {outputpath}')
 
resourceList = json.load(open("../resourceList.json", "r"))

class KnowledgeBase:
    def __init__(self, provider):
        self.provider = provider
        self.fileViewConstructed = False
        self.fileViewRetrieved = False
        self.fileViewObtained = False
        self.fileView = defaultdict()
        self.repoViewConstructed = False
        self.repoViewRetrieved = False
        self.repoViewObtained = False
        self.repoView = defaultdict()
        self.repoTypeView = defaultdict()
        self.repoListView = defaultdict()
        self.repoDefaultView = defaultdict(list)
        self.repoDependencyView = defaultdict(list)
        self.repoImportanceView = defaultdict(list)
        self.repoTrivialView = defaultdict(list)
        self.schemaViewConstructed = False
        self.schemaViewRetrieved = False
        self.schemaViewObtained = False
        self.schemaView = defaultdict()
        self.schemaDetailView = defaultdict()
        self.schemaCompleteView = defaultdict()
        self.registryViewConstructed = False
        self.registryViewRetrieved = False
        self.registryViewObtained = False
        self.registryView = defaultdict(list)
        
    def __str__(self):
        result = "Provider is {self.provider}\n"
        result += "Repo view: \n"
        for resourceType in self.repoView:
            result += "resourceType: " + resourceType + "\n"
            for resourceAttr in self.repoView[resourceType]:
                result += "    resourceAttr: " + resourceAttr + "\n"
                for resourceAttrValue in self.repoView[resourceType][resourceAttr]:
                    result += "        resourceAttrValue: " + resourceAttrValue + "\n"
        result += "Schema view: \n"
        for resourceType in self.repoView:
            result += "resourceType: " + resourceType + "\n"
            for resourceAttr in self.repoView[resourceType]:
                result += "    resourceAttr: " + resourceAttr + "\n"
                for resourceAttrValue in self.repoView[resourceType][resourceAttr]:
                    result += "        resourceAttrValue: " + resourceAttrValue + "\n"
        return result
    
    def constructFileView(self, inputDirectory, outputDirectory):
        self.fileViewConstructed = True
        getRegoFormat.instrumentRegoPolicies(inputDirectory, outputDirectory, regoFileCommandString, headerString, 10000)
    
    def retrieveFileView(self, directory, jsonDirectory, KBFileName):
        if self.fileViewConstructed == False:
            print("You have to construct file view first!")
            return self.fileView
        self.fileViewRetrieved = True
        if not os.path.exists(jsonDirectory):
            os.mkdir(jsonDirectory)
        utils.execute_cmd_imm(f"rm -rf {jsonDirectory}/*")
        arglists = []
        count = 0
        for filename in os.listdir(directory):
            count += 1
            filepath = os.path.join(directory, filename)
            MDCPath = os.path.join(jsonDirectory, filename[:-5]+"_FileView.json")
            arglists.append([filepath, count, MDCPath])
        pool = multiprocessing.Pool(processes=8)
        for arglist in arglists:
            pool.apply_async(call_regoMDCCount, args=arglist)
        pool.close()
        pool.join()
        
        for jsonFilename in os.listdir(jsonDirectory):
            try:
                jsonFilepath = os.path.join(jsonDirectory, jsonFilename)
                jsonData = json.load(open(jsonFilepath, "r"))
                tempList = jsonData["result"][0]["expressions"][0]["value"]
                if "_FileView.json" in jsonFilepath:
                    for resourceType, resourceAttr, resourceAttrVal in tempList:
                        if resourceType not in self.fileView:
                            self.fileView[resourceType] = defaultdict()
                        if resourceAttr not in self.fileView[resourceType]:
                            self.fileView[resourceType][resourceAttr] = defaultdict(int)
                        self.fileView[resourceType][resourceAttr][resourceAttrVal] += 1
            except:
                print("Something went wrong when executing opa command!", jsonFilepath)
        with open(KBFileName, 'w') as f:
            json.dump(self.fileView, f, indent = 4)
        return self.fileView
    
    def constructRepoView(self, inputDirectory, outputDirectory):
        self.repoViewConstructed = True
        getRegoFormat.instrumentRegoMinimalDep(inputDirectory, outputDirectory, regoRepoCommandString, headerString, 50000)
    
    def retrieveRepoView(self, directory, jsonDirectory, KBFileName, KBDefaultFileName, KBDependencyFileName, KBImportanceFileName):
        if self.repoViewConstructed == False:
            print("You have to construct repo view first!")
            return self.repoView
        self.repoViewRetrieved = True
        if not os.path.exists(jsonDirectory):
            os.mkdir(jsonDirectory)
        utils.execute_cmd_imm(f"rm -rf {jsonDirectory}/*")
        arglists = []
        arglists_default = []
        arglists_dependency = []
        arglists_config = []
        count = 0
        for filename in os.listdir(directory):
            count += 1
            filepath = os.path.join(directory, filename)
            MDCPath = os.path.join(jsonDirectory, filename[:-5]+"_RepoView.json")
            defaultValuePath = os.path.join(jsonDirectory, filename[:-5]+"_DefaultValue.json")
            dependencyPath = os.path.join(jsonDirectory, filename[:-5]+"_Dependency.json")
            configPath = os.path.join(jsonDirectory, filename[:-5]+"_Config.json")
            arglists.append([filepath, count, MDCPath])
            arglists_default.append([filepath, count, defaultValuePath])
            arglists_dependency.append([filepath, count, dependencyPath])
            arglists_config.append([filepath, count, configPath])
        pool = multiprocessing.Pool(processes=8)
        for arglist in arglists:
            pool.apply_async(call_regoMDCCount, args=arglist)
        for arglist in arglists_default:
            pool.apply_async(call_regoDefaultValue, args=arglist)
        for arglist in arglists_dependency:
            pool.apply_async(call_regoDependency, args=arglist)
        for arglist in arglists_config:
            pool.apply_async(call_regoConfigValue, args=arglist)
        pool.close()
        pool.join()
        
        # tempCountIndex = 0
        tempCountDict = defaultdict(int)
        tempValueDict = defaultdict()
        for jsonFilename in os.listdir(jsonDirectory):
            try:
                jsonFilepath = os.path.join(jsonDirectory, jsonFilename)
                jsonData = json.load(open(jsonFilepath, "r"))
                tempList = jsonData["result"][0]["expressions"][0]["value"]
                if "_RepoView.json" in jsonFilepath:
                    for resourceType, resourceAttr, resourceAttrVal in tempList:
                        if resourceType not in self.repoView:
                            self.repoView[resourceType] = defaultdict()
                        if resourceAttr not in self.repoView[resourceType]:
                            self.repoView[resourceType][resourceAttr] = defaultdict(int)
                        if resourceType not in self.repoTypeView:
                            self.repoTypeView[resourceType] = defaultdict()
                        if resourceAttr not in self.repoTypeView[resourceType]:
                            self.repoTypeView[resourceType][resourceAttr] = type(resourceAttrVal)
                        if resourceType not in self.repoListView:
                            self.repoListView[resourceType] = defaultdict()
                        if resourceAttr not in self.repoListView[resourceType]:
                            self.repoListView[resourceType][resourceAttr] = []
                        if type(resourceAttrVal) == self.repoTypeView[resourceType][resourceAttr]:
                            self.repoView[resourceType][resourceAttr][resourceAttrVal] += 1  
                            if resourceAttrVal not in self.repoListView[resourceType][resourceAttr]:
                                self.repoListView[resourceType][resourceAttr].append(resourceAttrVal)
                elif "_DefaultValue" in jsonFilepath:
                    for resourceAddress in tempList:
                        resourceType = resourceAddress.split(".")[0]
                        for resourceAttr in tempList[resourceAddress]:
                            self.repoDefaultView[resourceType].append(resourceAttr)
                elif "_Dependency.json" in jsonFilepath:
                    for resourceType1, resourceType2, resourceAttr1, resourceAttr2 in tempList:
                        if (resourceType1, resourceType2, resourceAttr1, resourceAttr2) not in self.repoDependencyView[resourceType1]:
                            self.repoDependencyView[resourceType1].append((resourceType1, resourceType2, resourceAttr1, resourceAttr2))
                        if resourceType2 in resourceList and resourceType2 not in self.repoDependencyView:
                            self.repoDependencyView[resourceType2] = []
                elif "_Config" in jsonFilepath:
                    for resourceAddress in tempList:
                        resourceType = resourceAddress.split(".")[0]
                        for resourceAttr in tempList[resourceAddress]:
                            if resourceType not in tempValueDict:
                                tempValueDict[resourceType] = defaultdict(int)
                            tempValueDict[resourceType][resourceAttr] += 1
                        tempCountDict[resourceType] += 1
            except:
                print("Something went wrong when executing opa command!", jsonFilepath)
        ### fix default value logic, including not only default, but also "important" attributes
        for resourceType in tempValueDict:
            for resourceAttr in tempValueDict[resourceType]:
                if float(tempValueDict[resourceType][resourceAttr])/ tempCountDict[resourceType] >= 0.2:
                    if resourceType not in self.repoImportanceView:
                        self.repoImportanceView[resourceType] = []
                    if resourceAttr not in self.repoImportanceView[resourceType]:
                        self.repoImportanceView[resourceType].append(resourceAttr)
                else:
                    if resourceType not in self.repoTrivialView:
                        self.repoTrivialView[resourceType] = []
                    if resourceAttr not in self.repoTrivialView[resourceType]:
                        self.repoTrivialView[resourceType].append(resourceAttr)
        with open(KBFileName, 'w') as f:
            json.dump(self.repoView, f, sort_keys = True, indent = 4)
        with open(KBDefaultFileName, 'w') as f:
            json.dump(self.repoDefaultView, f, sort_keys = True, indent = 4)
        with open(KBDependencyFileName, 'w') as f:
            json.dump(self.repoDependencyView, f, sort_keys = True, indent = 4)
        with open(KBImportanceFileName, 'w') as f:
            json.dump(self.repoImportanceView, f, sort_keys = True, indent = 4)
        return self.repoView, self.repoListView, self.repoDefaultView, self.repoDependencyView, self.repoImportanceView, self.repoTrivialView
    
    def constructSchemaView(self, inputFile, outputFile):
        self.schemaViewConstructed = True
        fi = open(inputFile, "r")
        content = "mock_config := " + fi.read()  
        regoString = headerString + regoSchemaString + "\n" + content
        fi.close()
        fo = open(outputFile, "w")
        fo.write(regoString)
        fo.close()
    
    def retrieveSchemaView(self, fileName, jsonFileName, KBFileName, jsonDetailFileName, KBDetailFileName, jsonCompleteFileName, KBCompleteFileName):
        if self.schemaViewConstructed == False:
            print("You have to construct schema view first!")
            return self.schemaView
        self.schemaViewRetrieved = True
        call_regoMDCCount(fileName, 1, jsonFileName)
        call_regoSchemaDetail(fileName, 1, jsonDetailFileName)
        call_regoSchemaComplete(fileName, 1, jsonCompleteFileName)
        jsonFilepath = os.path.join("./", jsonFileName)
        jsonData = json.load(open(jsonFilepath, "r")) 
        try:
            self.schemaView = jsonData["result"][0]["expressions"][0]["value"]
        except:
            print("Something went wrong when executing opa command!", jsonFilepath)
        with open(KBFileName, 'w') as f:
            json.dump(self.schemaView, f, sort_keys = True, indent = 4)
            
        jsonDetailFilepath = os.path.join("./", jsonDetailFileName)
        jsonDetailData = json.load(open(jsonDetailFilepath, "r")) 
        try:
            schemaDetailView = jsonDetailData["result"][0]["expressions"][0]["value"]
            for resourceType in schemaDetailView: 
                if resourceType not in resourceList:
                    continue    
                self.schemaDetailView[resourceType] = defaultdict()
                for item in schemaDetailView[resourceType]:
                    attributeName = item[0]
                    reqOrOpt = item[1]
                    if reqOrOpt != "nested":
                        self.schemaDetailView[resourceType][attributeName] = reqOrOpt
                    else:
                        min_items = item[2]
                        if min_items == 0:
                            self.schemaDetailView[resourceType][attributeName] = "optional"
                        else:
                            self.schemaDetailView[resourceType][attributeName] = "required"
        except:
            print("Something went wrong when executing opa command!", jsonDetailFilepath)
        with open(KBDetailFileName, 'w') as f:
            json.dump(self.schemaDetailView, f, sort_keys = True, indent = 4)
        
        jsonCompleteFilepath = os.path.join("./", jsonCompleteFileName)
        jsonCompleteData = json.load(open(jsonCompleteFilepath, "r")) 
        try:
            schemaCompleteView = jsonCompleteData["result"][0]["expressions"][0]["value"]
            for resourceType in schemaCompleteView:
                if resourceType not in resourceList:
                    continue  
                self.schemaCompleteView[resourceType] = defaultdict()
                for attributeName, schemaType in schemaCompleteView[resourceType]:
                    self.schemaCompleteView[resourceType][attributeName] = schemaType
        except:
            print("Something went wrong when executing opa command!", jsonCompleteFilepath)
        with open(KBCompleteFileName, 'w') as f:
            json.dump(self.schemaCompleteView, f, sort_keys = True, indent = 4)
        
        return self.schemaDetailView
    
    def constructGPTView(self, GPTFile, repoFile, outputFile):
        self.schemaViewConstructed = True
        fiGPT = open(GPTFile, "r")
        fiRepo = open(repoFile, "r")
        contentGPT = "mock_config_GPT := " + fiGPT.read()
        contentRepo = "mock_config_repo := " + fiRepo.read()
        regoString = headerString + regoGPTString + "\n" + contentGPT + "\n" + contentRepo
        fiGPT.close()
        fiRepo.close()
        fo = open(outputFile, "w")
        fo.write(regoString)
        fo.close()
    
    def constructRegistryView(self, inputDirectory, outputDirectory):
        self.registryViewConstructed = True
        if not os.path.exists(outputDirectory):
            os.mkdir(outputDirectory)
        getRegoFormat.instrumentRegoMinimalDep(inputDirectory, outputDirectory, regoRegistryCommandString, headerString, 50000)
    
    def retrieveRegistryView(self, directory, jsonDirectory, KBFileName):
        if self.registryViewConstructed == False:
            print("You have to construct registry view first!")
            return self.repoView
        self.registryViewRetrieved = True
        if not os.path.exists(jsonDirectory):
            os.mkdir(jsonDirectory)
        utils.execute_cmd_imm(f"rm -rf {jsonDirectory}/*")
        arglists = []
        count = 0
        for filename in os.listdir(directory):
            count += 1
            filepath = os.path.join(directory, filename)
            MDCPath = os.path.join(jsonDirectory, filename[:-5]+"_RegistryView.json")
            arglists.append([filepath, count, MDCPath])
        pool = multiprocessing.Pool(processes=8)
        for arglist in arglists:
            pool.apply_async(call_regoMDCCount, args=arglist)
        pool.close()
        pool.join()
        
        for jsonFilename in os.listdir(jsonDirectory):
            try:
                jsonFilepath = os.path.join(jsonDirectory, jsonFilename)
                jsonData = json.load(open(jsonFilepath, "r"))
                tempList = jsonData["result"][0]["expressions"][0]["value"]
                if "_RegistryView.json" in jsonFilepath:
                    for resourceType1, resourceType2, resourceAttr1, resourceAttr2 in tempList:
                        if (resourceType1, resourceType2, resourceAttr1, resourceAttr2) not in self.registryView[resourceType1]:
                            self.registryView[resourceType1].append((resourceType1, resourceType2, resourceAttr1, resourceAttr2))
            except:
                print("Something went wrong when executing opa command!", jsonFilepath)
        with open(KBFileName, 'w') as f:
            json.dump(self.registryView, f, sort_keys = True, indent = 4)
        return self.registryView
    
def removeDuplicate(valueDict, attrName, item):
    if item == None:
        return False
    for currItem in valueDict[attrName]:
        if not isinstance(currItem, str):
            continue
        if item in currItem and item != currItem:
            return True
        elif currItem in item:
            valueDict[attrName].remove(currItem)
            valueDict[attrName].append(item)
            return True
        elif item.capitalize() == currItem.capitalize():
            if item.capitalize() != item:
                return True
            else:
                valueDict[attrName].remove(currItem)
                valueDict[attrName].append(item)
                return True
    return False

def getProviderSchema(resourceProvider):
    ### construct schema view first. This is required for filtering out optional variable
    providerName = resourceProvider.split("-")[-1]
    AzureKnowledgeBase = KnowledgeBase(resourceProvider)
    AzureKnowledgeBase.constructSchemaView(f"../schemaFiles/{providerName}.json", f"../schemaFiles/{providerName}.rego")
    AzureKnowledgeBase.retrieveSchemaView(f"../schemaFiles/{providerName}.rego", f"../schemaFiles/{providerName}_result.json", f"../schemaFiles/{providerName}KBSchemaView.json", \
                                          f"../schemaFiles/{providerName}_resultDetail.json", f"../schemaFiles/{providerName}KBSchemaDetailView.json", \
                                          f"../schemaFiles/{providerName}_resultComplete.json", f"../schemaFiles/{providerName}KBSchemaCompleteView.json")
def getProviderRegistry(resourceProvider):
    ### construct global dependency graph to acquire all reference types.
    AzureKnowledgeBase = KnowledgeBase(resourceProvider)
    if not os.path.exists(f"../regoFiles/{resourceProvider}"):
        os.mkdir(f"../regoFiles/{resourceProvider}")
    AzureKnowledgeBase.constructRegistryView(f"../regoFiles/{resourceProvider}/outputRegoPlanHandledFormat", f"../regoFiles/{resourceProvider}/outputRegoRegistryViewFormula")
    AzureKnowledgeBase.retrieveRegistryView(f"../regoFiles/{resourceProvider}/outputRegoRegistryViewFormula", f"../regoFiles/{resourceProvider}/outputRegoRegistryViewResult", \
                                            f"../regoFiles/{resourceProvider}/KBRegistryView.json")

def determineValue(resourceType, resourceProvider):
    resourceProvider = resourceProvider.split("-")[-1]
    AzureKnowledgeBase = KnowledgeBase(resourceProvider)
    AzureKnowledgeBase.constructRepoView(f"../regoFiles/{resourceType}/outputRegoPlanHandledFormat", f"../regoFiles/{resourceType}/outputRegoRepoViewFormula")
    KBRepoView, KBRepoListView, KBRepoDefaultView, KBRepoDependencyView, KBRepoImportanceView, KBRepoTrivialView = AzureKnowledgeBase.retrieveRepoView(f"../regoFiles/{resourceType}/outputRegoRepoViewFormula", f"../regoFiles/{resourceType}/outputRegoRepoViewResult", \
                                                                     f"../regoFiles/{resourceType}/KBRepoView.json", f"../regoFiles/{resourceType}/KBDefaultView.json", f"../regoFiles/{resourceType}/KBDependencyView.json", f"../regoFiles/{resourceType}/KBImportanceView.json")
    valueDict = defaultdict(list)
    valueUnfilteredDict = defaultdict(list)
    jsonData = json.load(open(f"../schemaFiles/{resourceProvider}KBSchemaDetailView.json", "r"))
    jsonCompleteData = json.load(open(f"../schemaFiles/{resourceProvider}KBSchemaCompleteView.json", "r"))
    repoListView = defaultdict()
    repoStringListView = defaultdict()
    repoDefaultView = defaultdict()
    repoDependencyView = defaultdict()
    repoReferenceView = defaultdict()
    repoImportanceView = defaultdict()
    repoTrivialView = defaultdict()
    
    ### get repo dependency view, this is used to explore references among resources.
    if os.path.exists('../regoFiles/repoDependencyView.json'):
        repoDependencyView = json.load(open('../regoFiles/repoDependencyView.json'))
    for oneType in KBRepoDependencyView:
        if oneType not in resourceList:
            continue
        if oneType not in repoDependencyView:
            repoDependencyView[oneType] = []
        for referenceTuple in KBRepoDependencyView[oneType]:
            if referenceTuple[1] not in resourceList or referenceTuple[3] not in referenceTuple[2]:
                continue
            if list(referenceTuple) not in repoDependencyView[oneType]:
                repoDependencyView[oneType].append(list(referenceTuple))
    for oneType in resourceList:
        if oneType not in repoDependencyView:
            repoDependencyView[oneType] = []
    with open('../regoFiles/repoDependencyView.json', 'w') as f:
        json.dump(repoDependencyView, f, sort_keys = True, indent = 4)
        
    if os.path.exists('../regoFiles/repoReferenceView.json'):
        repoReferenceView = json.load(open('../regoFiles/repoReferenceView.json'))
    for oneType in KBRepoDependencyView:
        if oneType not in resourceList:
            continue
        if oneType not in repoReferenceView:
            repoReferenceView[oneType] = []
        for referenceTuple in KBRepoDependencyView[oneType]:
            if referenceTuple[1] not in resourceList or referenceTuple[3] not in referenceTuple[2]:
                continue
            referenceStringList = referenceTuple[2].split(".")
            if len(referenceStringList) == 1:
                referenceName = referenceStringList[0]
            else:
                referenceName = referenceStringList[0] + "." + referenceStringList[-1]
                
            if referenceName not in repoReferenceView[oneType]:
                repoReferenceView[oneType].append(referenceName)
    for oneType in resourceList:
        if oneType not in repoReferenceView:
            repoReferenceView[oneType] = []
    with open('../regoFiles/repoReferenceView.json', 'w') as f:
        json.dump(repoReferenceView, f, sort_keys = True, indent = 4)
        
    ### get repo default view, this is used to explore attributes with default values.
    if os.path.exists('../regoFiles/repoDefaultView.json'):
        repoDefaultView = json.load(open('../regoFiles/repoDefaultView.json'))
    for oneType in KBRepoDefaultView:
        if oneType not in resourceList:
            continue
        if oneType not in repoDefaultView:
            repoDefaultView[oneType] = []
        for oneAttr in KBRepoDefaultView[oneType]:
            if oneAttr in jsonCompleteData[oneType] and (jsonCompleteData[oneType][oneAttr] == "block" or jsonCompleteData[oneType][oneAttr] == "list"):
                continue
            if oneAttr not in repoDefaultView[oneType] and "tag" not in oneAttr:
                repoDefaultView[oneType].append(oneAttr)
    for oneType in resourceList:
        if oneType not in repoDefaultView:
            repoDefaultView[oneType] = []
    with open('../regoFiles/repoDefaultView.json', 'w') as f:
        json.dump(repoDefaultView, f, sort_keys = True, indent = 4)
    
    ### get repo importance view, this is used to explore attributes that are important.
    if os.path.exists('../regoFiles/repoImportanceView.json'):
        repoImportanceView = json.load(open('../regoFiles/repoImportanceView.json'))
    for oneType in KBRepoImportanceView:
        if oneType != resourceType:
            continue
        if oneType not in repoImportanceView:
            repoImportanceView[oneType] = []
        for oneAttr in KBRepoImportanceView[oneType]:
            if oneAttr not in repoImportanceView[oneType] and "tag" not in oneAttr:
                repoImportanceView[oneType].append(oneAttr)
    for oneType in resourceList:
        if oneType not in repoImportanceView:
            repoImportanceView[oneType] = []
    with open('../regoFiles/repoImportanceView.json', 'w') as f:
        json.dump(repoImportanceView, f, sort_keys = True, indent = 4)
                   
    ### get repo trivial view, this is used to explore attributes that are trivial.
    if os.path.exists('../regoFiles/repoTrivialView.json'):
        repoTrivialView = json.load(open('../regoFiles/repoTrivialView.json'))
    for oneType in KBRepoTrivialView:
        if oneType != resourceType:
            continue
        if oneType not in repoTrivialView:
            repoTrivialView[oneType] = []
        for oneAttr in KBRepoTrivialView[oneType]:
            if oneAttr not in repoTrivialView[oneType] and "tag" not in oneAttr:
                repoTrivialView[oneType].append(oneAttr)
    for oneType in resourceList:
        if oneType not in repoTrivialView:
            repoTrivialView[oneType] = []
    with open('../regoFiles/repoTrivialView.json', 'w') as f:
        json.dump(repoTrivialView, f, sort_keys = True, indent = 4)
    
    ### get repo list view, this is the first step towards random but reasonable test case mutation.
    if os.path.exists('../regoFiles/repoListView.json'):
        repoListView = json.load(open('../regoFiles/repoListView.json'))
    if os.path.exists('../regoFiles/repoStringListView.json'):
        repoStringListView = json.load(open('../regoFiles/repoStringListView.json'))
    for oneType in KBRepoListView:
        if oneType not in repoListView:
            repoListView[oneType] = defaultdict()
        if oneType not in repoStringListView:
            repoStringListView[oneType] = defaultdict()
        for oneAttr in KBRepoListView[oneType]:
            if oneAttr not in repoListView[oneType]:
                repoListView[oneType][oneAttr] = []
            if oneAttr not in repoStringListView[oneType]:
                repoStringListView[oneType][oneAttr] = []
            for oneValue in KBRepoListView[oneType][oneAttr]:
                if oneValue == "NULL":
                    oneValueHandled = None
                else:
                    oneValueHandled = oneValue
                if oneValueHandled not in repoListView[oneType][oneAttr]:
                    repoListView[oneType][oneAttr].append(oneValueHandled) 
                if oneValue == True:
                    oneValueString = "true"
                elif oneValue == False:
                    oneValueString = "false"
                elif oneValue == "NULL":
                    oneValueString = "null"
                else:
                    oneValueString = str(oneValue)
                if oneValueString not in repoStringListView[oneType][oneAttr]:
                    repoStringListView[oneType][oneAttr].append(oneValueString)
                    
    for oneType in resourceList:
        if oneType not in repoListView:
            repoListView[oneType] = defaultdict()
        if oneType not in repoStringListView:
            repoStringListView[oneType] = defaultdict()
            
    with open('../regoFiles/repoListView.json', 'w') as f:
        json.dump(repoListView, f, sort_keys = True, indent = 4)
    with open('../regoFiles/repoStringListView.json', 'w') as f:
        json.dump(repoStringListView, f, sort_keys = True, indent = 4)
    
    ### get repo view, this is the first step towards constant templating of rule mining.
    if resourceType not in KBRepoView:
        return
    def is_camel_case(s):
        return s != s.lower() and s != s.upper() and "_" not in s
    resourceTypeList = resourceType.split("_")
    resourceTypeCamelCase = "".join([item[0].upper()+item[1:] for item in resourceTypeList[1:]])
    
    for attrName in KBRepoView[resourceType]:
        for schemaAttrName in jsonData[resourceType]:
            if attrName == schemaAttrName:
                for item in KBRepoView[resourceType][attrName]:
                    valueUnfilteredDict[attrName].append(item)
                #if len(repoView[resourceType][attrName]) <= 5 and schemaAttrMode == "required":
                if len(KBRepoView[resourceType][attrName]) == 1 or "_name" in attrName or "_id" in attrName or "_key" in attrName or "/" in attrName or "_range" in attrName or \
                    "_uri" in attrName or ("_address" in attrName and "_address_" not in attrName) or (".name" in attrName and "sku" not in attrName) or ".address" in attrName or "id" in attrName:
                    continue
                elif len(KBRepoView[resourceType][attrName]) <= 6:
                    for item in KBRepoView[resourceType][attrName]:
                        if removeDuplicate(valueDict, attrName, item) == True:
                            continue
                        if type(item) == int:
                            continue
                        elif type(item) == str and ("." in item or "/" in item or "*" in item):
                            continue
                        elif item == "NULL":
                            valueDict[attrName].append(None)
                        elif type(item) == bool or (len(item) <= 30 and len(item) >= 1 and "hold" not in item):
                            valueDict[attrName].append(item)
                elif "size" in attrName or "location" in attrName or "sku" in attrName:
                    for item in KBRepoView[resourceType][attrName]:
                        if removeDuplicate(valueDict, attrName, item) == True:
                            continue
                        if type(item) == int:
                            continue
                        elif item == "NULL":
                            valueDict[attrName].append(None)
                        elif type(item) == bool or (len(item) <= 30 and len(item) > 1 and "hold" not in item):
                            valueDict[attrName].append(item)
                elif "name" in attrName:
                    for item in KBRepoView[resourceType][attrName]:
                        if resourceTypeCamelCase in item and is_camel_case(item) and item[0].upper() == item[0] and len(item) <= 30 and "-" not in item and "1" not in item and "Test" not in item:
                            valueDict[attrName].append(item)
                        elif item == "NULL":
                            valueDict[attrName].append(None)
                elif "priority" in attrName:
                    for item in KBRepoView[resourceType][attrName]:
                        if len(valueDict[attrName]) >= 1:
                            continue
                        valueDict[attrName].append(None)
                elif  "offer" in attrName or "version" in attrName or "publisher" in attrName:
                    for item in KBRepoView[resourceType][attrName]:
                        if KBRepoView[resourceType][attrName][item] >= 8:
                            valueDict[attrName].append(item)
                elif len(KBRepoView[resourceType][attrName]) > 5:
                    for item in KBRepoView[resourceType][attrName]:
                        if item == "NULL":
                            valueDict[attrName].append(None)
                    
    with open(f'../regoFiles/{resourceType}/filteredRepoView.json', 'w') as f:
        json.dump(valueDict, f, sort_keys = True, indent = 4)
    with open(f'../regoFiles/{resourceType}/unfilteredRepoView.json', 'w') as f:
        json.dump(valueUnfilteredDict, f, sort_keys = True, indent = 4)
    repoView = defaultdict()
    if os.path.exists('../regoFiles/repoView.json'):
        repoView = json.load(open('../regoFiles/repoView.json'))
    repoView[resourceType] = valueDict
    with open('../regoFiles/repoView.json', 'w') as f:
        json.dump(repoView, f, sort_keys = True, indent = 4)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource_name", help="the name of the resource we want to get")
    parser.add_argument("--resource_provider", help="the name of the resource provider we want to get")
    args = parser.parse_args()
    return args
    
if __name__ == "__main__":
    args = parse_args()
    if not os.path.exists("../schemaFiles"):
        os.mkdir("../schemaFiles")
    if str(args.resource_name) != "SCHEMA" and str(args.resource_name) != "PROVIDER":
        ### Usage example: python3 -u regoMVPGetKnowledgeBase.py --resource_name azurerm_application_gateway --resource_provider terraform-provider-azurerm
        if str(args.resource_name) != "ALL":
            determineValue(str(args.resource_name), str(args.resource_provider))
        else:
            for resourceName in resourceList:
                determineValue(resourceName, str(args.resource_provider))
    elif str(args.resource_name) == "PROVIDER":
        ### Usage example: time python3 -u regoMVPGetKnowledgeBase.py --resource_name PROVIDER --resource_provider terraform-provider-azurerm
        getProviderRegistry(str(args.resource_provider))
    else:
        ### Must run this bfore the main knowledge base generation function!
        ### Usage example: time python3 -u regoMVPGetKnowledgeBase.py --resource_name SCHEMA --resource_provider terraform-provider-azurerm
        getProviderSchema(str(args.resource_provider))