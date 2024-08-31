### Handle Terraform child modules on the rego level. This preprocessing step has to be used after getRegoFormat
import os
from collections import defaultdict
import sys
sys.path.insert(0, '..')
import utils.utils as utils
import glob
import json
import argparse
import knowledgeBaseConstruction.regoMVPGetKnowledgeBase as regoMVPGetKnowledgeBase

headerString = """
package assemble
import data.fugue.resource_view.resource_view_input
import future.keywords.in
"""

def replaceString(obj, stringOld, stringNew):
    def decode_dict(a_dict):
        for key, value in a_dict.items():
            try:
                print(stringNew, key, value, isinstance(stringNew, str))
                if isinstance(stringNew, str):
                    a_dict[key] = value.replace(stringOld, stringNew)
                elif isinstance(stringNew, bool):
                    a_dict[key] = stringNew
            except AttributeError:
                print("Unrecognized type in replaceString function!")
        return a_dict

    return json.loads(json.dumps(obj), object_hook=decode_dict)

def variablePopulate(regoFile, jsonFile, tempFile, inputFile, outputFile, popoulateMethod):
    startString = ""
    jsonString = ""
    try:
        with open(regoFile, "r") as f:
            line = f.readline()
            startFlag = 0 
            while line:
                if "mock_config := {" in line:
                    startFlag = 1
                    startString += "mock_config := "
                    jsonString += "{\n"
                elif startFlag == 0:
                    startString += line
                elif startFlag == 1:
                    jsonString += line
                line = f.readline()
        with open(jsonFile, "w") as f:
            f.write(jsonString)
        
    except Exception as e:
        print("Something went wrong when grabbing terraform plan rego data", e)
        with open(outputFile, "w") as f:
            f.write(startString + jsonString)
        return False
    try:
        jsonData = json.load(open(jsonFile, "r"))
        with open(inputFile, 'w') as f:
            json.dump(jsonData, f, sort_keys = True, indent = 4)
        with open(inputFile, "r") as f:
            jsonString = f.read()
        with open(inputFile, "w") as f:
            f.write(startString + jsonString)
        configuration = jsonData["configuration"]
        planned_values = jsonData["planned_values"]
        planned_root_module = planned_values["root_module"]
        planned_root_resoures = planned_root_module["resources"]
        planned_root_child_modules = planned_root_module["child_modules"]
        root_module = configuration["root_module"]
        root_resources = root_module["resources"]
        module_calls = root_module["module_calls"]
    except Exception as e:
        print("Something went wrong when grabbing terraform plan json data", e)
        with open(outputFile, "w") as f:
            f.write(startString + jsonString)
        return False
    try:
        for planned_module in planned_root_child_modules:
            resources = planned_module["resources"]
            for resource in resources:
                planned_root_resoures.append(resource)
    except:
        print("Something went wrong when grabbing planned_value data")
        with open(outputFile, "w") as f:
            f.write(startString + jsonString)
        return False
    for key in module_calls:
        mapping_resource_names = defaultdict()
        resourceString = ""
        try:
            module_call = module_calls[key]
            expressions = module_call["expressions"]
            module_name = key
            module = module_call["module"]
        except:
            #print("Something went wrong when grabbing child module calls")
            continue
        
        try:
            resources = module["resources"]
        except:
            resources = []
        try:
            variables =  module["variables"]
        except:
            variables = []
        ### Core logic to reveal the true name of resources within each modules
        for resource in resources:
            resource_address = resource["address"]
            mapping_resource_names[resource_address] = "module." + module_name + "." + resource_address
        with open(tempFile, 'w') as f:
            json.dump(resources, f, sort_keys = True, indent = 4)
        with open(tempFile, "r") as f:
            resourceString = f.read()
            for findString, replaceString in mapping_resource_names.items():
                resourceString = resourceString.replace("\"" + findString + "\"", "\"" + replaceString + "\"")
                resourceString = resourceString.replace("\"" + findString + ".", "\"" + replaceString + ".")
        with open(tempFile, 'w') as f:
            f.write(resourceString)
        with open(tempFile, 'r') as f:
            resources = json.load(f)
            
        ### Core logic to populate module call inputs into module resource attributes.
        if popoulateMethod == "naive":
            mapping_constants = defaultdict()
            mapping_references = defaultdict()
            for variable in variables:
                if variable in expressions:
                    if "constant_value" in expressions[variable]:
                        constant_value = expressions[variable]["constant_value"]
                        mapping_constants["var."+variable] = constant_value
                    elif "references" in expressions[variable]:
                        references = expressions[variable]["references"]
                        #references.sort(key = lambda x: len(x)) 
                        mapping_references["var."+variable] = references
            with open(tempFile, 'w') as f:
                json.dump(resources, f, sort_keys = True, indent = 4)
            with open(tempFile, "r") as f:
                resourceString = f.read()
                for findString, replaceString in mapping_constants.items():
                    oldString = f'"references": ["{findString}"]'
                    #newString = ""
                    if isinstance(replaceString, str):
                        newString = f'"constant_value": "{replaceString}"'
                    elif isinstance(replaceString, bool):
                        if replaceString == True:
                            newString = f'"constant_value": true'
                        else:
                            newString = f'"constant_value": false'
                    elif isinstance(replaceString, list):
                        tempList = ["\""+item+"\"" for item in replaceString]
                        listString = ",".join(tempList)
                        newString = f'"constant_value": [{listString}]'
                    else:
                        newString = f'"constant_value": "{replaceString}"'
                        print("Type", type(replaceString))
                    resourceString = resourceString.replace(oldString, newString)
                for findString, replaceStrings in mapping_references.items():
                    oldString = f'"{findString}"'
                    wrappedStrings = ["\"" + item + "\"" for item in replaceStrings]
                    newString = ",".join(wrappedStrings)
                    resourceString = resourceString.replace(oldString, newString)
            with open(tempFile, 'w') as f:
                f.write(resourceString)
                
        elif popoulateMethod == "identify":
            mapping_varname = defaultdict()
            mapping_references = defaultdict()
            for variable in variables:
                if variable in expressions:
                    varname_old = "var."+variable
                    varname_new = "root."+module_name+"."+variable
                    mapping_varname[varname_old] = varname_new
                    if "references" in expressions[variable]:
                        references = expressions[variable]["references"]
                        #references.sort(key = lambda x: len(x)) 
                        mapping_references["var."+variable] = references
            with open(tempFile, 'w') as f:
                json.dump(resources, f, sort_keys = True, indent = 4)
            with open(tempFile, "r") as f:
                resourceString = f.read()
                for findString, replaceStrings in mapping_references.items():
                    oldString = f'"{findString}"'
                    wrappedStrings = ["\"" + item + "\"" for item in replaceStrings]
                    newString = ",".join(wrappedStrings)
                    resourceString = resourceString.replace(oldString, newString)
                for oldString, newString in mapping_varname.items():
                    resourceString = resourceString.replace(oldString, newString)
            with open(tempFile, 'w') as f:
                f.write(resourceString)
        try:
            resources = json.load(open(tempFile, "r"))
            for resource in resources:
                root_resources.append(resource)
        except:
            continue
    print("Success")
    with open(jsonFile, 'w') as f:
        json.dump(jsonData, f, sort_keys = True, indent = 4)
    with open(jsonFile, "r") as f:
        jsonString = f.read()
    with open(outputFile, "w") as f:
        f.write(startString + jsonString)
    return True

def getPlannedValues(inputFile, outputFile):
    try:
        jsonData = json.load(open(inputFile, "r"))
        configuration = jsonData["planned_values"]
        root_module = configuration["root_module"]
        child_modules = root_module["child_modules"]
        resourceAll = []
        for child_module in child_modules:
            resources = child_module["resources"]
            resourceAll += resources
            
        with open(outputFile, 'w') as f:
            json.dump(resourceAll, f, sort_keys = True, indent = 4)
        return resourceAll
    except:
        return []

def generateHandledRego(directory):
    configuration = variablePopulate(f"{directory}/plan_json.rego",f"{directory}/plan.json", f"{directory}/config_populated.json", f"{directory}/unhandled.rego", f"{directory}/handled.rego", "identify")
    planned_values = getPlannedValues(f"{directory}/plan.json", f"{directory}/planned_values.json")
    regoFormat = defaultdict(list)
    for resource in configuration:
        address = resource["address"]
        regoFormat[address].append(resource)
    for resource in planned_values:
        address = resource["address"]
        regoFormat[address].append(resource)
    with open(f"{directory}/handled.rego", 'w') as f:
        json.dump(regoFormat, f, sort_keys = True, indent = 4)
    with open(f"{directory}/handled.rego", 'r') as f:
        regoString = f.read()
        regoString = headerString + "\n" + "resourceDict := " + regoString
    with open(f"{directory}/handled.rego", 'w') as f:
        f.write(regoString)
    return regoFormat


def generateHandledByResource(resourceType, existing):
    receiverDir = f"../regoFiles/{resourceType}/outputRegoPlanHandledFormat"
    if not os.path.exists(receiverDir):
        os.mkdir(receiverDir)
    utils.execute_cmd_imm(f"rm -rf {receiverDir}/*")
    if existing == "false":
        inputDirName = f"../folderFiles/folders_{resourceType}_filtered"
        for filename in os.listdir(inputDirName):
            f = os.path.join(inputDirName, filename)
            tfDirectories = utils.execute_cmd_imm(f"find {f} -name \"plan_json.rego\"")
            mainTFFiles = tfDirectories.split("\n")[:-1]
            for mainTFFile in mainTFFiles:
                mainDir = mainTFFile[:utils.find_nth(mainTFFile,"/",-1)]
                print(mainDir)
                relevant = utils.execute_cmd_imm(f"grep -Rnw '{mainDir}' -e '{resourceType}'")
                if not relevant or relevant == "Failure":
                    print("Irrelevant dir, please move on!")
                    continue
                variablePopulate(f"{mainDir}/plan_json.rego", f"{mainDir}/plan_handling.json", f"{mainDir}/plan_temp.json", f"{mainDir}/unhandled.rego", f"{mainDir}/handled.rego", "identify")
                name = "_".join(mainDir.split("/")[-1:])
                utils.execute_cmd_imm(f"cp {mainDir}/handled.rego {receiverDir}/{name}.rego")
    else:
        inputDirName = f"../regoFiles/{resourceType}/outputRegoPlanFormat"
        handleFolder = f"../regoFiles/{resourceType}/handleFolder"
        if not os.path.exists(handleFolder):
            os.mkdir(handleFolder)
        for filename in os.listdir(inputDirName):
            utils.execute_cmd_imm(f"rm -rf {handleFolder}/*")
            f = os.path.join(inputDirName, filename)
            utils.execute_cmd_imm(f"cp {f} {handleFolder}/plan_json.rego")
            relevant = utils.execute_cmd_imm(f"grep -Rnw '{handleFolder}' -e '{resourceType}'")
            # print("relevance", relevant)
            if not relevant or relevant == "Failure":
                print("Irrelevant dir, please move on!")
                continue
            variablePopulate(f"{handleFolder}/plan_json.rego", f"{handleFolder}/plan_handling.json", f"{handleFolder}/plan_temp.json", f"{handleFolder}/unhandled.rego", f"{handleFolder}/handled.rego", "identify")
            utils.execute_cmd_imm(f"cp {handleFolder}/handled.rego {receiverDir}/{filename}")

def generateHandledByRegistry(registryType, existing):
    receiverDir = f"../regoFiles/{registryType}/outputRegoPlanHandledFormat"
    if not os.path.exists(f"../regoFiles/{registryType}"):
        os.mkdir(f"../regoFiles/{registryType}")
    if not os.path.exists(receiverDir):
        os.mkdir(receiverDir)
    utils.execute_cmd_imm(f"rm -rf {receiverDir}/*")
    #resourceList = regoMVPGetKnowledgeBase.resourceList
    resourceList = json.load(open("../resourceList.json", "r"))
    ### both folders examples and usageExamples need to be processed!
    for inputDirName in [f"{registryType}/examples", f"{registryType}/usageExamples"]:
        for filename in os.listdir(inputDirName):
            f = os.path.join(inputDirName, filename)
            tfDirectories = utils.execute_cmd_imm(f"find {f} -name \"plan_json.rego\"")
            mainTFFiles = tfDirectories.split("\n")[:-1]
            for mainTFFile in mainTFFiles:
                mainDir = mainTFFile[:utils.find_nth(mainTFFile,"/",-1)]
                print(mainDir)
                name = "provider_" + "_".join(mainDir.split("/")[2:])
                if existing == "false":
                    variablePopulate(f"{mainDir}/plan_json.rego", f"{mainDir}/plan_handling.json", f"{mainDir}/plan_temp.json", f"{mainDir}/unhandled.rego", f"{mainDir}/handled.rego", "identify")
                    utils.execute_cmd_imm(f"cp {mainDir}/handled.rego {receiverDir}/{name}.rego")
                for resourceType in resourceList:
                    relevant = utils.execute_cmd_imm(f"grep -Rnw '{mainDir}' -e '{resourceType}'")
                    if not relevant or relevant == "Failure":
                        continue
                    if not os.path.exists(f"../regoFiles/{resourceType}"):
                        continue
                    if not os.path.exists(f"../folderFiles/folders_{resourceType}_filtered"):
                        continue
                    else:
                        utils.execute_cmd_imm(f"cp {mainDir}/handled.rego ../regoFiles/{resourceType}/outputRegoPlanHandledFormat/{name}.rego")
                        if not os.path.exists(f"../folderFiles/folders_{resourceType}_filtered/{name}"):
                            utils.execute_cmd_imm(f"cp -r {f} ../folderFiles/folders_{resourceType}_filtered/{name}")
                        else:
                            utils.execute_cmd_imm(f"rm -rf ../folderFiles/folders_{resourceType}_filtered/{name}")
                            utils.execute_cmd_imm(f"cp -r {f} ../folderFiles/folders_{resourceType}_filtered/{name}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource_name", help="the name of the resource we want to get")
    parser.add_argument("--existing", help="get rego configs from existing rego folder", nargs='?', default = "false")
    args = parser.parse_args()
    return args

### Usage example 1: time python3 -u getModuleContent.py --resource_name ALL --existing true
### Usage example 2: time python3 -u getModuleContent.py --resource_name azurerm_application_gateway --existing true
### Usage example 3: time python3 -u getModuleContent.py --resource_name terraform-provider-azurerm --existing true
if __name__ == "__main__":
    args = parse_args()
    if "terraform-provider" not in args.resource_name:
        if str(args.resource_name) != "ALL":
            generateHandledByResource(str(args.resource_name), str(args.existing))
        else:
            resourceList = json.load(open("../resourceList.json", "r"))
            for resourceName in resourceList:
                generateHandledByResource(resourceName, str(args.existing))
    else:
        generateHandledByRegistry(str(args.resource_name), str(args.existing))
    