import os
import sys
sys.path.insert(0, '..')
import utils.utils as utils
import json
from collections import defaultdict
import multiprocessing
import dataPreprocessing.getRegoFormat as getRegoFormat
import knowledgeBaseConstruction.regoMVPGetKnowledgeBase as regoMVPGetKnowledgeBase
import regoTemplateAttr
import regoTemplateTopo
import regoTemplateCombo
import regoTemplateSingle
import regoMVPRule
import csv
import argparse

headerString = """
package assemble
import data.fugue.resource_view.resource_view_input
import future.keywords.in
"""

resultCountString = """
resultCount[rule] := counts {
    rule := resultList[_]
    counts := count({id | resultList[id] == rule})
}  
"""
with open(f"../regoFiles/repoView.json", "r") as f:
    repoViewString = f.read()
with open(f"../regoFiles/globalAncestorDict.json", "r") as f:
    globalAncestorDictString = f.read()
        
regoPlanDependencyCommand = "repoViewTop := " + repoViewString + "\n" + \
                            "globalAncestorDict := " + globalAncestorDictString + "\n"+ \
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
    any([type1 in globalAncestorDict[resourceTypeLabel], type1 == resourceTypeLabel])
    walk(config[id1], [path1, value1])
    address2 := config[id2]["address"]
    type2 := config[id2]["type"]
    type2 in object.keys(repoViewTop)
    any([type2 in globalAncestorDict[resourceTypeLabel], type2 == resourceTypeLabel])
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
    any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    edges := {neighbor | artificialDependencyList[e][0] == address; neighbor := artificialDependencyList[e][1]}
}

artificialAncestorDict[address] := reachable {
    address := config[n]["address"]
    type := config[n]["type"]
    any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    reachable := graph.reachable(artificialPredDict, [address])
}

referencesPredDict[address] := edges {
    address := config[n]["address"]
    type := config[n]["type"]
    any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    edges := {neighbor | dependencyList[e][0] == address; neighbor := dependencyList[e][1]}
}

combinedPredDict[address] := edges {
    address := config[n]["address"]
    type := config[n]["type"]
    any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    edges := {neighbor | neighbor := artificialPredDict[address][_]} | {neighbor | neighbor := referencesPredDict[address][_]}
}

referencesSuccDict[address] := edges {
    address := config[n]["address"]
    type := config[n]["type"]
    any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    edges := {neighbor | dependencyList[e][1] == address; neighbor := dependencyList[e][0]}
}

ancestorDict[address] := reachable {
    address := config[n]["address"]
    type := config[n]["type"]
    any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    reachable := graph.reachable(combinedPredDict, [address])
}

naiveAncestorDict[address] := reachable {
    address := config[n]["address"]
    type := config[n]["type"]
    any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    reachable := graph.reachable(referencesPredDict, [address])
}

offspringDict[address] := reachable {
    address := config[n]["address"]
    type := config[n]["type"]
    any([type in globalAncestorDict[resourceTypeLabel], type == resourceTypeLabel])
    reachable := graph.reachable(referencesSuccDict, [address])
}

resourceDict[address] := [address_config, address_plan] {
    address := config[a]["address"]
    address == plan[b]["address"]
    address_config := config[a]
    address_plan := plan[b]
}
"""

with open('../regoFiles/globalPredecessorDict.json', 'r') as f:
    predecessorDict = json.load(f)

def call_regoRuleResultCount(filepath, count, outputpath):
    result = utils.execute_cmd_imm(f'timeout 160 opa eval -d {filepath} "data.assemble.resultCount" > {outputpath}')
    print(count, filepath, result)
    
def findAncestors(resourceType, result):
    if resourceType in result or "data." in resourceType:
        return
    result += [resourceType]
    for node in predecessorDict[resourceType]:
        findAncestors(node, result)
    print("Find ancestors result:", result)

### Construct schema info from TF cloud provider schema files, mainly for optional v.s. computed v.s. required etc.
def constructSchemaInfo(schemaFile, resourceType):
    jsonData = json.load(open(schemaFile, "r"))
    resourceDetails = jsonData[resourceType]
    resourceDetailsDict = defaultdict()
    for idAttr, idAttrType, attrSchemaType in resourceDetails:
        resourceDetailsDict[idAttr] = [idAttrType, attrSchemaType]
    with open(f'../tflint/zodiac/outputRuleCount/resourceDetails_{resourceType}.json', 'w') as f:
        json.dump(resourceDetailsDict, f, sort_keys = True, indent = 4)
    with open(f'../tflint/zodiac/outputRuleCount/resourceDetails_{resourceType}.json', 'r') as f:
        resourceDetailsString = "resourceDetail := " + f.read() + "\n"
    return resourceDetailsString

### Rule Template class, the primary class for candidate rule extraction from repos
class RuleTemplate:
    def __init__(self, operator, resourceType):
        self.operator = operator
        self.resourceType = resourceType
        self.candidateRuleArguments = []
        self.candidateRules = []
        self.constructed = False
        self.retrieved = False
        self.obtained = False
        self.ruleID = 0
        self.ratio = 1
        self.threshold = 100
        
    def __str__(self):
        print(self.operator)
    
    ### Construct rego extraction statements from a wide variety of implemented templates
    def constructRegoRule(self, schemaFile, inputDirectory, outputDirectory, resourceType):
        self.constructed = True
        ancestors = []
        findAncestors(resourceType, ancestors)
        ancestorString = ["\"" + item + "\"" for item in ancestors]
        ancestorCommand = "ancestorList := [" + ",".join(ancestorString) + "]\n"
        
        if self.operator == "ATTR":
            regoRuleCommand, regoRuleNameList = regoTemplateAttr.constructRegoAttr(resourceType, "Attr")
            if len(regoRuleNameList) < 1:
                print("Incomplete rule template! Please check the ATTR operator")
        elif self.operator == "SINGLE":
            regoRuleCommand, regoRuleNameList = regoTemplateSingle.constructRegoSingle(resourceType, "Single")
            if len(regoRuleNameList) < 1:
                print("Incomplete rule template! Please check the SINGLE operator")
        elif self.operator == "TOPO":
            regoRuleCommand1, regoRuleNameList1 = regoTemplateTopo.constructRegoTopo1(resourceType, "Topo")
            #regoRuleCommand2, regoRuleNameList2 = regoTemplateTopo.constructRegoTopo2(resourceType, "Topo")
            regoRuleCommand = regoRuleCommand1
            regoRuleNameList = regoRuleNameList1
            if len(regoRuleNameList) < 1:
                print("Incomplete rule template! Please check the TOPO operator")
        elif self.operator == "COMBO":
            regoRuleCommand1, regoRuleNameList1 = regoTemplateCombo.constructRegoCombo1(resourceType, "Combo")
            regoRuleCommand2, regoRuleNameList2 = regoTemplateCombo.constructRegoCombo2(resourceType, "Combo")
            regoRuleCommand = regoRuleCommand1 + regoRuleCommand2
            regoRuleNameList = regoRuleNameList1 + regoRuleNameList2
            if len(regoRuleNameList) < 1:
                print("Incomplete rule template! Please check the COMBO operator")
        else:
            print("Rule template operator hasn't been implemented yet!")
            regoRuleCommand, regoRuleNameList = "", []
        
        if len(regoRuleNameList) < 1:
            return
        regoAggregateCommand = ""
        for index, regoRuleName in enumerate(regoRuleNameList):
            if index == 0:
                regoAggregateCommand += f"rule{index+1} := {regoRuleName}\n"
            else:
                regoAggregateCommand += f"rule{index+1} := array.concat(rule{index}, {regoRuleName})\n"
        lenList = len(regoRuleNameList)
        regoAggregateCommand += f"resultList := rule{lenList}"
        regoAggregateCommand += resultCountString
        regoResourceTypeCommand = f'resourceTypeLabel := "{resourceType}"\n'
        regoCommandString = regoResourceTypeCommand + regoPlanDependencyCommand + ancestorCommand + regoRuleCommand + regoAggregateCommand
        getRegoFormat.instrumentRegoMinimalDep(inputDirectory, outputDirectory, regoCommandString, headerString, 5000)
    
    ### retrieve rego outputs as results containing candidate rules extracted, paralleled for performance
    ### a simple heuristic to determine the "support" value threshold for different resource types
    def retrieveRegoRule(self, directory, jsonDirectory):
        if self.constructed == False:
            print("You have to construct rego rules first!")
            return self.candidateRuleArguments
        self.retrieved = True
        if not os.path.exists(jsonDirectory):
            os.mkdir(jsonDirectory)
        utils.execute_cmd_imm(f"rm -rf {jsonDirectory}/*")
        arglists = []
        count = 0
        for filename in sorted(list(os.listdir(directory))):
            count += 1
            filepath = os.path.join(directory, filename)
            referencePath = os.path.join(jsonDirectory, filename[:-5]+"_ruleCount.json")
            arglists.append([filepath, count, referencePath])
        pool = multiprocessing.Pool(processes=16)
        for arglist in arglists:
            pool.apply_async(call_regoRuleResultCount, args=arglist)
        pool.close()
        pool.join()

        ruleCounter = defaultdict(int)
        for jsonFilename in os.listdir(jsonDirectory):
            try:
                jsonFilepath = os.path.join(jsonDirectory, jsonFilename)
                jsonData = json.load(open(jsonFilepath, "r"))
                tempCounter = jsonData["result"][0]["expressions"][0]["value"]
                if "_ruleCount.json" in jsonFilepath:
                    for rule in tempCounter:
                        ruleCounter[rule] += tempCounter[rule]
            except:
                print("Something went wrong when executing opa command!", jsonFilepath)

        lRuleCounter = defaultdict(int)
        lRuleArray = list()
        for key in ruleCounter:
            print("Initial rules: ", key, ruleCounter[key])
            lRuleArray.append([ruleCounter[key], key])
        lRuleArray.sort(reverse=True)
        lRuleArray = lRuleArray[:self.threshold]
        for _, key in lRuleArray:
            candidateRule = [item.split(" ") for item in key.split(" #### ")]
            operationList = candidateRule[0][0].split("If")
            operationList = operationList[0].split("Then")
            if operationList[-1] in ["Absence", "Existence", "Constant", "Equal", "Unequal", "CIDRInclude", "CIDRExclude", "Enum", "CIDRMask"]:
                lRuleCounter[key] = ruleCounter[key]
                self.candidateRuleArguments.append(candidateRule)
            else:
                if count/(ruleCounter[key]) <= 200:
                    lRuleCounter[key] = ruleCounter[key]
                    self.candidateRuleArguments.append(candidateRule)
        if not os.path.exists(f"../regoFiles/outputRuleCount"):
            os.mkdir(f"../regoFiles/outputRuleCount")
        with open(f'../regoFiles/outputRuleCount/ruleCount_{self.resourceType}_{self.operator}.json', 'w') as f:
            json.dump(lRuleCounter, f, sort_keys = True, indent = 4)
        print(self.candidateRuleArguments)
        return self.candidateRuleArguments

def obtainCandidateRules(candidateRuleArguments, operator):
    ruleID = 0
    candidateRules = []
    for ruleArguments in candidateRuleArguments:
        ruleID += 1
        candidateRule = regoMVPRule.Rule(operator, ruleID)
        print("Obtain rule arguments:", ruleArguments)
        candidateRule.initiate(ruleArguments)
        candidateRules.append(candidateRule)
    return candidateRules

### infrastructure for candidate rule extraction test cases
def testRuleTemplate(operator, resourceType, threshold=500):
    if not os.path.exists(f"../regoFiles/{resourceType}/{operator}/"):
        os.mkdir(f"../regoFiles/{resourceType}/{operator}")
    utils.execute_cmd_imm(f"rm -rf ../regoFiles/{resourceType}/{operator}/*")
    ruleTemplate = RuleTemplate(operator, resourceType)
    ruleTemplate.threshold = threshold
    ruleTemplate.constructRegoRule("../schemaFiles/azurermKBSchemaDetailView.json", f"../regoFiles/{resourceType}/outputRegoPlanHandledFormat", f"../regoFiles/{resourceType}/{operator}/outputRegoRuleFormula", resourceType)
    ruleTemplate.retrieveRegoRule(f"../regoFiles/{resourceType}/{operator}/outputRegoRuleFormula", f"../regoFiles/{resourceType}/{operator}/outputRegoRuleResult")
    fields = ['Operator', 'Shape', 'Operand1', 'Operand2', 'Operand3', 'Operand4', 'Operand5', 'Operand6', 'Operand7', 'Operand8']
    rows = []
    candidateRules = obtainCandidateRules(ruleTemplate.candidateRuleArguments, operator)
    for rule in candidateRules:
        rows.append([rule.operator, rule.shape, rule.operand1, rule.operand2, rule.operand3, rule.operand4, rule.operand5, rule.operand6, rule.operand7, rule.operand8])
    if not os.path.exists(f"../csvFiles/{resourceType}/"):
        os.mkdir(f"../csvFiles/{resourceType}")
    with open(f"../csvFiles/{resourceType}/{operator}.csv", 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)
    if not os.path.exists(f"../plainTextFiles/{resourceType}/"):
        os.mkdir(f"../plainTextFiles/{resourceType}")
    
    return candidateRules

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource_type", help="the type of the resource we want to get")
    parser.add_argument("--operation_type", help="the type of the operation we want to extract")
    parser.add_argument("--threshold", help="get rules ranked by frequency to a certain threshold", nargs='?', default = "200")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    resourceList = regoMVPGetKnowledgeBase.resourceList
    if not os.path.exists(f"../csvFiles/"):
        os.mkdir(f"../csvFiles/")
    if not os.path.exists(f"../plainTextFiles/"):
        os.mkdir(f"../plainTextFiles/")
        
    if args.resource_type == "TEST" and args.operation_type == "ALL":
        ### Usage example: time python3 -u regoMVPRuleTemplate.py --resource_type TEST --operation_type ALL --threshold 1000 
        for resource in resourceList:
            candidateRules = testRuleTemplate("ATTR", resource, int(args.threshold))
            candidateRules = testRuleTemplate("TOPO", resource, int(args.threshold))
            candidateRules = testRuleTemplate("COMBO", resource, int(args.threshold))
    elif args.resource_type == "TEST" and args.operation_type == "COUNT":
        totalCount = 0
        for resouce in resourceList:
            directory = f"../csvFiles/{resouce}"
            for filename in sorted(list(os.listdir(directory))):
                filepath = os.path.join(directory, filename)
                numLines = sum(1 for _ in open(filepath))
                totalCount += numLines
        print("Total candidate rules: ", totalCount)
    else:
        ### Usage example: time python3 -u regoMVPRuleTemplate.py --resource_type azurerm_application_gateway --operation_type ATTR --threshold 1000 > output2
        ### Usage example: time python3 -u regoMVPRuleTemplate.py --resource_type azurerm_application_gateway --operation_type COMBO --threshold 1000 > output3
        ### Usage example: time python3 -u regoMVPRuleTemplate.py --resource_type azurerm_application_gateway --operation_type TOPO --threshold 1000 > output4
        candidateRules = testRuleTemplate(args.operation_type, args.resource_type, int(args.threshold))
    