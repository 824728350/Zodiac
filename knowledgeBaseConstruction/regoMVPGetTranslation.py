### Main entry to translate crawled programs into JSON format and store 
### them in the knowlwedge base. This is critical for the subsequent steps
### because test case generation only works with Terraform in JSON format.
import sys
import os
sys.path.insert(0, '..')
sys.path.insert(0, '../ruleTemplateInstantiation')
import utils.utils as utils
import json
import hcl2
from utils.utils import *
from collections import defaultdict
import multiprocessing
import dataPreprocessing.getRegoFormat as getRegoFormat
import argparse
import regoMVPGetKnowledgeBase
import traceback
import random
import string

headerString = """
package assemble
import data.fugue.resource_view.resource_view_input
import future.keywords.in
"""

### The definitio here is quite different from the one in template generation: we want to capture everything!
with open(f"../regoFiles/repoView.json", "r") as f:
    repoViewString = f.read()
regoPlanDependencyCommand = "repoViewTop := " + repoViewString + "\n" + \
"""
plan := object.get(mock_config.planned_values.root_module, "resources", [])
config := object.get(mock_config.configuration.root_module, "resources", [])

# childPlannedModules :=  object.get(mock_config.planned_values.root_module, "child_modules", [])
# rootPlan := object.get(mock_config.planned_values.root_module, "resources", [])
# childPlan := [item |
#    item := childPlannedModules[_].resources[_]
# ]
# plan := array.concat(rootPlan, childPlan)
# childConfigedModules :=  object.get(mock_config.configuration.root_module, "child_modules", [])
# rootConfig := object.get(mock_config.configuration.root_module, "resources", [])
# childConfig := [item |
#    item := childConfigedModules[_].resources[_]
# ]
# config := array.concat(rootConfig, childConfig)

dependencyDeprecatedList := [[address1, address2, idAttr1] |
    walk(config[id1], [path1, value1])
    address1 := config[id1]["address"]
    address2 := config[id2]["address"]
    id1 != id2
    "references" == path1[count(path1)-1]
    address2 in value1
    attr1 := [elem |
        elem := path1[n]
        n > 0; n < count(path1)-1
        is_string(elem)
    ]
    idAttr1 := concat(".", attr1)
]

dependencyList := [[address1, address2, idAttr1, idAttr2, idAttrSlice1, idAttrSlice2] |
    address1 := config[id1]["address"]
    type1 := config[id1]["type"]
    type1 in object.keys(repoViewTop)
    #any([type1 in globalAncestorDict[resourceTypeLabel], type1 == resourceTypeLabel])
    walk(config[id1], [path1, value1])
    address2 := config[id2]["address"]
    type2 := config[id2]["type"]
    type2 in object.keys(repoViewTop)
    #any([type2 in globalAncestorDict[resourceTypeLabel], type2 == resourceTypeLabel])
    id1 != id2
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
    idAttrListSlice1 := array.slice(attr1, 0, count(attr1)-1)
    idAttrSlice1 := concat(".", idAttrListSlice1)
    idAttr2 := trim_prefix(value1, idAddr2)
    any([idAttr2 == "name", idAttr2 == "id"])
    any([contains(idAttr1, "_name"), contains(idAttr1, "_id")])
    idAttrList2 := split(idAttr2, ".")
    idAttrListSlice2 := array.slice(idAttrList2, 0, count(idAttrList2)-1)
    idAttrSlice2 := concat(".", idAttrListSlice2)
]

inclusiveDependencyList := [[address1, address2, idAttr1, idAttr2, idAttrSlice1, idAttrSlice2] |
    address1 := config[id1]["address"]
    type1 := config[id1]["type"]
    #type1 in object.keys(repoViewTop)
    #any([type1 in globalAncestorDict[resourceTypeLabel], type1 == resourceTypeLabel])
    walk(config[id1], [path1, value1])
    address2 := config[id2]["address"]
    type2 := config[id2]["type"]
    #type2 in object.keys(repoViewTop)
    #any([type2 in globalAncestorDict[resourceTypeLabel], type2 == resourceTypeLabel])
    id1 != id2
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
    idAttrListSlice1 := array.slice(attr1, 0, count(attr1)-1)
    idAttrSlice1 := concat(".", idAttrListSlice1)
    idAttr2 := trim_prefix(value1, idAddr2)
    #any([idAttr2 == "name", idAttr2 == "id"])
    #any([contains(idAttr1, "_name"), contains(idAttr1, "_id")])
    idAttrList2 := split(idAttr2, ".")
    idAttrListSlice2 := array.slice(idAttrList2, 0, count(idAttrList2)-1)
    idAttrSlice2 := concat(".", idAttrListSlice2)
]

artificialDependencyList := [[address1, address2] |
    address1 := config[id1]["address"]
    address2 := config[id2]["address"]
    id1 != id2
    depends_on := config[id1]["depends_on"]
    address2 in depends_on
]

artificialPredDict[address] := edges {
    address := config[n]["address"]
    type := config[n]["type"]
    #any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    edges := {neighbor | artificialDependencyList[e][0] == address; neighbor := artificialDependencyList[e][1]}
}

artificialAncestorDict[address] := reachable {
    address := config[n]["address"]
    type := config[n]["type"]
    #any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    reachable := graph.reachable(artificialPredDict, [address])
}

referencesPredDict[address] := edges {
    address := config[n]["address"]
    type := config[n]["type"]
    #any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    edges := {neighbor | dependencyList[e][0] == address; neighbor := dependencyList[e][1]}
}

combinedPredDict[address] := edges {
    address := config[n]["address"]
    type := config[n]["type"]
    #any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    edges := {neighbor | neighbor := artificialPredDict[address][_]} | {neighbor | neighbor := referencesPredDict[address][_]}
}

inclusivePredDict[address] := edges {
    address := config[n]["address"]
    type := config[n]["type"]
    #any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    edges := {neighbor | inclusiveDependencyList[e][0] == address; neighbor := inclusiveDependencyList[e][1]}
}

referencesSuccDict[address] := edges {
    address := config[n]["address"]
    type := config[n]["type"]
    #any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    edges := {neighbor | dependencyList[e][1] == address; neighbor := dependencyList[e][0]}
}

ancestorDict[address] := reachable {
    address := config[n]["address"]
    type := config[n]["type"]
    #any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    reachable := graph.reachable(combinedPredDict, [address])
}

inclusiveAncestorDict[address] := reachable {
    address := config[n]["address"]
    type := config[n]["type"]
    #any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    reachable := graph.reachable(inclusivePredDict, [address])
}

naiveAncestorDict[address] := reachable {
    address := config[n]["address"]
    type := config[n]["type"]
    #any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    reachable := graph.reachable(referencesPredDict, [address])
}

offspringDict[address] := reachable {
    address := config[n]["address"]
    type := config[n]["type"]
    #any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    reachable := graph.reachable(referencesSuccDict, [address])
}

resourceDict[address] := [address_config, address_plan] {
    address := config[a]["address"]
    address == plan[b]["address"]
    address_config := config[a]
    address_plan := plan[b]
}
"""

### Translate repos from terraform hcl format into pure json format. This step
### is essential because right now there is no easy way for us to mutate hcl files
### directly. we tried several tools such as hcledit but they worked poorly.
def hcl2jsonTranslation(inputDirName, outputDirName, resourceDetail):
    try:
        utils.execute_cmd_imm(f"rm -rf {outputDirName}")
        utils.execute_cmd_imm(f"cp -r {inputDirName} {outputDirName}")
        utils.execute_cmd_imm(f"rm -rf {outputDirName}/*.rego")
        utils.execute_cmd_imm(f"rm -rf {outputDirName}/*.tfplan")
        utils.execute_cmd_imm(f"rm -rf {outputDirName}/.terraform*")
        utils.execute_cmd_imm(f"rm -rf {outputDirName}/*.json")
        
        tfFiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(f"{outputDirName}")) for f in fn]
        flagComplex = False
        for tfFile in tfFiles:
            if ".tf" != tfFile[-3:]:
                continue
            try:
                with open(f'{tfFile}', 'r') as f:
                    dictValue = hcl2.load(f)
            except:
                print("hcl2 load failed because the terraform file is doing something strange")
                continue
            if "module" in dictValue:
                flagComplex = True
            ### handle some special cases where json format cannot process as expected
            if "resource" in dictValue:
                for resourceBlock in dictValue["resource"]:
                    for resourceType in resourceBlock:
                        for resourceInstance in resourceBlock[resourceType]:
                            for resourceAttribute in list(resourceBlock[resourceType][resourceInstance].keys()):
                                if resourceAttribute in ["security_rule", "route", "subnet", "rule"]:
                                    if resourceType not in resourceDetail:
                                        resourceBlock[resourceType][resourceInstance][resourceAttribute] = []
                                    else:
                                        for attrCandidate in resourceDetail[resourceType]:
                                            attrCandidateList = attrCandidate.split(".")
                                            if len(attrCandidateList) == 2 and resourceAttribute == attrCandidateList[0]:
                                                for attrBlock in resourceBlock[resourceType][resourceInstance][resourceAttribute]:
                                                    if attrCandidateList[1] not in attrBlock:
                                                        attrBlock[attrCandidateList[1]] = None
                                if "vhd" in resourceAttribute:
                                    flagComplex = True
                                elif resourceAttribute == "count" or resourceAttribute == "for_each":
                                    flagComplex = True
                                elif resourceAttribute == "depends_on":
                                    tempList = resourceBlock[resourceType][resourceInstance][resourceAttribute][:]
                                    resourceBlock[resourceType][resourceInstance][resourceAttribute] = []
                                elif resourceAttribute in ["lifecycle", "domain_name_label", "tags"]:
                                    del(resourceBlock[resourceType][resourceInstance][resourceAttribute])
                                
                                elif type(resourceBlock[resourceType][resourceInstance][resourceAttribute]) == str and "\n" in resourceBlock[resourceType][resourceInstance][resourceAttribute]:
                                    del(resourceBlock[resourceType][resourceInstance][resourceAttribute])
                                elif type(resourceBlock[resourceType][resourceInstance][resourceAttribute]) == str and ("substr" in resourceBlock[resourceType][resourceInstance][resourceAttribute] or "replace" in resourceBlock[resourceType][resourceInstance][resourceAttribute]):
                                    repString = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
                                    resourceBlock[resourceType][resourceInstance][resourceAttribute] = repString
                                    
            if "variable" in dictValue:
                for variableBlock in dictValue["variable"]:
                    for variableInstance in variableBlock:
                        if "type" in variableBlock[variableInstance]:
                            del(variableBlock[variableInstance]["type"])
                        elif "validation" in variableBlock[variableInstance]:
                            del(variableBlock[variableInstance]["validation"])
                            
            with open(f'{tfFile}.json', 'w') as f:
                json.dump(dictValue, f, sort_keys = True, indent = 4)
            utils.execute_cmd_imm(f"rm -rf {tfFile}")
        
        jsonFiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(f"{outputDirName}")) for f in fn]
        countJsonList = []
        for jsonFile in jsonFiles:
            if ".tf.json" not in jsonFile:
                continue
            countJsonList.append(jsonFile)
        
        hclFiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(f"{outputDirName}")) for f in fn]
        countHCLList = []
        for hclFile in hclFiles:
            if ".tf" != hclFile[-3:]:
                continue
            countHCLList.append(hclFile)
        if len(countJsonList)==0 or len(countHCLList)>0:
            flagComplex = True
        if flagComplex == True:
            utils.execute_cmd_imm(f"rm -rf {outputDirName}")
    except:
        print("Something went wrong when trying to translate hcl into json format")
        traceback.print_exc()

def regoGetLocalKnowledge(outputDirName, resourceType):
    regoResourceTypeCommand = f'resourceTypeLabel := "{resourceType}"\n'
    getRegoFormat.instrumentRegoMinimalDep(outputDirName, outputDirName, regoResourceTypeCommand+ regoPlanDependencyCommand, headerString, 5000)
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.plan" > {outputDirName}/plan.json')
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.config" > {outputDirName}/config.json')
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.dependencyList" > {outputDirName}/dependencyList.json')
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.referencesPredDict" > {outputDirName}/referencesPredDict.json')
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.referencesSuccDict" > {outputDirName}/referencesSuccDict.json')
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.offspringDict" > {outputDirName}/offspringDict.json')
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.ancestorDict" > {outputDirName}/ancestorDict.json')
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.artificialDependencyList" > {outputDirName}/artificialDependencyList.json')
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.naiveAncestorDict" > {outputDirName}/naiveAncestorDict.json')
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.inclusiveAncestorDict" > {outputDirName}/inclusiveAncestorDict.json')
    utils.execute_cmd_imm(f'timeout 80 opa eval -d {outputDirName}/handled.rego "data.assemble.inclusiveDependencyList" > {outputDirName}/inclusiveDependencyList.json')

### For a specific rego folder, retrieve both json format and rego knowledge.
def formatTranslationSingle(resourceType, hclDirectory, jsonDirectory, knowledgeDirectory, filename, resourceDetail, index = 0):
    print("Translation: ", filename, index)
    try:
        inputDirName = os.path.join(hclDirectory, filename)
        outputDirName = os.path.join(jsonDirectory, filename)
        hcl2jsonTranslation(inputDirName, outputDirName, resourceDetail)
    except Exception as e:
        print("Something went wrong when trying to translate hcl into json format", filename, e)
    try:
        outputDirName = os.path.join(knowledgeDirectory, filename)
        if not os.path.exists(outputDirName):
            os.mkdir(outputDirName)
        utils.execute_cmd_imm(f"rm -rf {outputDirName}/*")
        utils.execute_cmd_imm(f"cp ../regoFiles/{resourceType}/outputRegoPlanHandledFormat/{filename}.rego {outputDirName}/handled.rego")
        regoGetLocalKnowledge(outputDirName, resourceType)
    except Exception as e:
        print("Something went wrong when trying to get local knowledge from rego files", e)

### Do the above translation in batch, putting all result into ../folderFiles   
def formatTranslationBatchProcessing(resourceType):
    with open(f"../schemaFiles/azurermKBSchemaDetailView.json", "r") as f:
        resourceDetail = json.load(f)
    hclDirectory = f"../folderFiles/folders_{resourceType}_filtered"
    jsonDirectory = f"../folderFiles/folders_{resourceType}_json"
    knowledgeDirectory = f"../folderFiles/folders_{resourceType}_knowledge"
    if not os.path.exists(jsonDirectory):
        os.mkdir(jsonDirectory)
    if not os.path.exists(knowledgeDirectory):
        os.mkdir(knowledgeDirectory)
    index = 0
    arglists = []
    for filename in os.listdir(hclDirectory):
        index += 1
        arglists.append([resourceType, hclDirectory, jsonDirectory, knowledgeDirectory, filename, resourceDetail, index])
        #formatTranslationSingle(resourceType, hclDirectory, jsonDirectory, knowledgeDirectory, filename, resourceDetail, index)
    pool = multiprocessing.Pool(processes=16)
    for arglist in arglists:
        pool.apply_async(formatTranslationSingle, args=arglist)
    pool.close()
    pool.join()       

### For each repo, get the mapping between rego format and json format. This is useful for the later on
### positive/negative test case generation post processing phases.
def formatMappingSingle(resourceType, jsonDirectory, knowledgeDirectory, resultDirectory, filename, index=0):
    print("Mapping: ", filename, index)
    try:
        jsonDirName = os.path.join(jsonDirectory, filename)
        knowledgeDirName = os.path.join(knowledgeDirectory, filename)
        outputDirName = os.path.join(resultDirectory, filename)
        if not os.path.exists(outputDirName):
            os.mkdir(outputDirName)
        if not os.path.exists(jsonDirName) or not os.path.exists(knowledgeDirName):
            print("Missing essential directories!")
            return
        else:
            resourceDict = defaultdict(list)
            typeDict = defaultdict(list)
            planJsonData = json.load(open(f"{knowledgeDirName}/plan.json", "r"))
            plan = planJsonData["result"][0]["expressions"][0]["value"]
            for _, resourceBlock in enumerate(plan):
                resourceName = resourceBlock["address"]
                if "module." not in resourceName:
                    identifier = resourceName
                    resourceDict[identifier].append(resourceBlock)
                    
            #tfFileString = utils.execute_cmd_imm(f"find {jsonDirName} -name \"*.tf.json\"")
            #tfFiles = tfFileString.split("\n")[:-1]
            tfFiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(f"{jsonDirName}")) for f in fn]
            for tfFile in tfFiles:
                if ".tf.json" not in tfFile:
                    continue
                resourceJsonData = json.load(open(f"{tfFile}", "r"))
                if "resource" not in resourceJsonData:
                    continue
                for resourceList in resourceJsonData["resource"]:
                    for resourceType in resourceList:
                        for resourceName in resourceList[resourceType]:
                            resourceBlock = resourceList[resourceType][resourceName]
                            if "module." not in resourceName:
                                identifier = resourceType + "." + resourceName
                                if identifier in resourceDict:
                                    resourceDict[identifier].append(resourceBlock)
            for identifier in list(resourceDict.keys()):
                if len(resourceDict[identifier]) != 2:
                    del resourceDict[identifier]
                else:
                    resourceType = identifier.split(".")[0]
                    typeDict[resourceType].append(resourceDict[identifier] + [filename])
            with open(f"{outputDirName}/mapping.json", 'w') as f:
                json.dump(resourceDict, f, indent = 4)
            with open(f"{outputDirName}/type.json", 'w') as f:
                json.dump(typeDict, f, indent = 4)
        #print("Success?")
    except Exception as e:
        print("Something went wrong when trying to find resource mapping among formats", e)

### Generating the above mapping in batch, also aggregate results based on resource types.
def formatMappingBatchProcessing(resourceType):
    jsonDirectory = f"../folderFiles/folders_{resourceType}_json"
    knowledgeDirectory = f"../folderFiles/folders_{resourceType}_knowledge"
    resultDirectory = f"../folderFiles/folders_{resourceType}_mapping"
    if not os.path.exists(jsonDirectory):
        os.mkdir(jsonDirectory)
    if not os.path.exists(knowledgeDirectory):
        os.mkdir(knowledgeDirectory)
    if not os.path.exists(resultDirectory):
        os.mkdir(resultDirectory)
    index = 0
    arglists = []
    for filename in os.listdir(jsonDirectory):
        index += 1
        arglists.append([resourceType, jsonDirectory, knowledgeDirectory, resultDirectory, filename, index])
    pool = multiprocessing.Pool(processes=16)
    for arglist in arglists:
        pool.apply_async(formatMappingSingle, args=arglist)
    pool.close()
    pool.join()  
    
    globalTypeFile = f"../folderFiles/globalType.json"
    if os.path.exists(globalTypeFile):
        globalTypeDict = json.load(open(f"{globalTypeFile}", "r"))
    else:    
        globalTypeDict = dict()
    for filename in os.listdir(jsonDirectory):
        try:
            if "provider" not in filename:
                continue
            outputDirName = os.path.join(resultDirectory, filename)
            typeJsonData = json.load(open(f"{outputDirName}/type.json", "r"))
            for resourceType in typeJsonData:
                if resourceType not in globalTypeDict:
                    globalTypeDict[resourceType] = []
                globalTypeDict[resourceType] += typeJsonData[resourceType]
        except Exception as e:
            print("Something went wrong when trying to aggregate global type dict", e)
    with open(f'{globalTypeFile}', 'w') as f:
        json.dump(globalTypeDict, f, sort_keys = True, indent = 4)
    
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", help="the translation action we want to take")
    parser.add_argument("--resource_name", help="the resource types we want to investigate")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    if str(args.action) == "TRANS" and str(args.resource_name) == "ALL":
        ### This must be executed before get partial order function!
        ### Usage example: time python3 -u regoMVPGetTranslation.py --action TRANS --resource_name ALL > output4
        for resourceType in regoMVPGetKnowledgeBase.resourceList:
            formatTranslationBatchProcessing(resourceType)
    elif str(args.action) == "TRANS":
        ### Usage example: time python3 -u regoMVPGetTranslation.py --action TRANS --resource_name azurerm_application_gateway
        formatTranslationBatchProcessing(str(args.resource_name))
    elif str(args.action) == "MAP" and str(args.resource_name) == "ALL":
        ### Usage example: time python3 -u regoMVPGetTranslation.py --action MAP --resource_name ALL > output5
        for resourceType in regoMVPGetKnowledgeBase.resourceList:
            formatMappingBatchProcessing(resourceType)
    elif str(args.action) == "MAP":
        ### Usage example: time python3 -u regoMVPGetTranslation.py --action MAP --resource_name azurerm_application_gateway
        formatMappingBatchProcessing(str(args.resource_name))