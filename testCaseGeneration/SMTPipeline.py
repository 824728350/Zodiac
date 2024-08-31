### Main entry for each specific validation iteration. Most implementation of false positive removal,
### true positive validation, and indistict check handling logic is defined here.
import sys
import os
sys.path.insert(0, '..')
sys.path.insert(0, '../ruleTemplateInstantiation')
import utils.utils as utils
import json
from utils.utils import *
import multiprocessing
import time
import SMTPostprocessing
import hashlib
import traceback
from SMTPreprocessing import *
import random
import argparse
        
### Validation pipeline entrance for each candiate sematic checks.       
def coreValidationPipeline(contextData, validatedRuleVault, candidateRuleVault = [], interpolationDataVault = [], original = True, iteration = 0, direction = True, resolve = False, interpolation = False):
    time.sleep(random.uniform(0,10))
    resourceType = contextData[0]
    targetRule = contextData[2]
    candidateRuleList = []
    validatedRuleList = []
    fg = open(f"../regoFiles/globalAncestorDict.json", "r")
    globalAncestor = json.load(fg)
    ruleFileList = [
                       f"../ruleJsonFiles/{resourceType}/ATTRFICL.json",
                       f"../ruleJsonFiles/{resourceType}/ATTRREFICL.json",
                       f"../ruleJsonFiles/{resourceType}/COMBOFICL.json",
                       f"../ruleJsonFiles/{resourceType}/COMBOREFICL.json",
                       f"../ruleJsonFiles/{resourceType}/TOPOFICL.json",
                       f"../ruleJsonFiles/{resourceType}/TOPOREFICL.json",
                   ]
    interRuleFileList = [
                       f"../interpolationFiles/{resourceType}/TOPOFIIN.json",
                       f"../interpolationFiles/{resourceType}/TOPOREFIIN.json",
                       f"../interpolationFiles/{resourceType}/COMBOFIIN.json",
                       f"../interpolationFiles/{resourceType}/COMBOREFIIN.json",
                       f"../interpolationFiles/{resourceType}/ATTRFIIN.json",
                       f"../interpolationFiles/{resourceType}/ATTRREFIIN.json",
                    ]
    testRule = None
    result = ""
    try:
        for ruleFileName in ruleFileList:
            ruleDataDict = json.load(open(ruleFileName, "r"))
            for statementKey in ruleDataDict:
                for ruleDetail, ruleString, manifest in ruleDataDict[statementKey]:
                    currentRule = ",".join(ruleDetail.split("####"))
                    candidateRuleList.append(ruleDetail.split("####"))
                    if targetRule in currentRule:
                        testRule = ruleDetail.split("####")
                        print("Test rule detail: ", testRule)
                        result = ruleDetail
        if interpolation == True:
            for ruleFileName in interRuleFileList:
                ruleDataDict = json.load(open(ruleFileName, "r"))
                for tempType, tempRule, _ in ruleDataDict:
                    if targetRule in tempRule:
                        testRule = tempRule.split(",")
                        result = tempRule
    except:
        print("Failed to open some of the mined rule files!")
        traceback.print_exc()
    if testRule == None:
        print("Cannot find a positive case to support the target rule! rule not known")
        return result, None
    if "Enum" in testRule[1] or "CIDRMask" in testRule[1] or "Count" in testRule[1]:
        print("Cannot find a positive case to support the target rule! operator not known")
        return result, None
    
    hashValueTemp = (int(hashlib.md5(("####".join(testRule)).encode('utf-8')).hexdigest(), 16)%10000000)
    
    if original == True:
        if not os.path.exists(f"../testFiles/validationFolders"):
            os.mkdir(f"../testFiles/validationFolders")
        validationDirectory = f"../testFiles/validationFolders/{resourceType}"
    elif interpolation == True:
        if not os.path.exists(f"../testFiles/validationFolders_{iteration}_inter_true"):
            os.mkdir(f"../testFiles/validationFolders_{iteration}_inter_true")
        validationDirectory = f"../testFiles/validationFolders_{iteration}_inter_true/{resourceType}"
    elif direction == True and resolve == True:
        if not os.path.exists(f"../testFiles/validationFolders_{iteration}_overlap_true"):
            os.mkdir(f"../testFiles/validationFolders_{iteration}_overlap_true")
        validationDirectory = f"../testFiles/validationFolders_{iteration}_overlap_true/{resourceType}"
    elif direction == True and resolve == False:
        if not os.path.exists(f"../testFiles/validationFolders_{iteration}_overlap_resolve"):
            os.mkdir(f"../testFiles/validationFolders_{iteration}_overlap_resolve")
        validationDirectory = f"../testFiles/validationFolders_{iteration}_overlap_resolve/{resourceType}"
    else:
        if not os.path.exists(f"../testFiles/validationFolders_{iteration}_overlap_false"):
            os.mkdir(f"../testFiles/validationFolders_{iteration}_overlap_false")
        validationDirectory = f"../testFiles/validationFolders_{iteration}_overlap_false/{resourceType}"
    if not os.path.exists(validationDirectory):
        os.mkdir(validationDirectory)
    
    ### Only consider rules that are from possible ancestor resources
    for valResourceType, valRuleDetail in validatedRuleVault:
        if "ThenExclusive" in testRule[1]:
            validatedRuleList.append(valRuleDetail.split(","))
        elif valResourceType in globalAncestor[resourceType] or valResourceType == resourceType:
            validatedRuleList.append(valRuleDetail.split(","))
    
    ### FIX ME: validated + candidate rule set, this is a temporary implementation
    filteredValidatedRuleList = []
    filteredCandidateRuleList = []
    for item in validatedRuleList:
        if item not in filteredValidatedRuleList:
            if interpolation == False and ("ThenAggParent" in item[1] or "ThenAggChild" in item[1] \
                or "ThenNonConstant" in item[1] or "ThenCIDRRange" in item[1]):
                    continue
            elif interpolation == True and "ThenAgg" in testRule[1] and "ThenAgg" in item[1]:
                continue
            if item == testRule:
                continue
            flagForbidden = False
            for ele in item:
                if ".private_ip_address " in ele:
                    flagForbidden = True
            if flagForbidden == True:
                continue
            filteredValidatedRuleList.append(item)
            
    if original == False:
        candidateRuleList = []
        for canResourceType, canRuleDetail in candidateRuleVault + interpolationDataVault:
            if "ThenExclusive" in testRule[1]:
                candidateRuleList.append(canRuleDetail.split(","))
            elif canResourceType in globalAncestor[resourceType] or canResourceType == resourceType:
                candidateRuleList.append(canRuleDetail.split(","))
                
    for item in candidateRuleList:
        if item not in filteredValidatedRuleList and item not in filteredCandidateRuleList:
            if interpolation == False and ("ThenNonConstant" in item[1]):
                continue
            elif interpolation == True and testRule[2] != item[2]:
                continue
            
            if item == testRule:
                continue
            flagForbidden = False
            for ele in item:
                if ".private_ip_address " in ele:
                    flagForbidden = True
            if flagForbidden == True:
                continue
            filteredCandidateRuleList.append(item)
    
    print("Comparison: ", len(filteredValidatedRuleList), len(filteredCandidateRuleList))
    for rule in filteredCandidateRuleList:
        print("Candidate rule:", rule)
    for rule in filteredValidatedRuleList:
        print("Validated rule:", rule)
    
    regoDirectory = f"../regoFiles/{resourceType}/outputRegoPlanHandledFormat"
    jsonDirectory = f"../folderFiles/folders_{resourceType}_json"
    mappingDirectory = f"../folderFiles/folders_{resourceType}_mapping"
    knowledgeDirectory = f"../folderFiles/folders_{resourceType}_knowledge"
    MDCDirectory = f"../folderFiles/folders_{resourceType}_mdc"
    GENDirectory = f"../folderFiles/folders_{resourceType}_gen"
    AGGDirectory = f"../folderFiles/folders_{resourceType}_agg"
    if not os.path.exists(MDCDirectory):
        os.mkdir(MDCDirectory)
    if not os.path.exists(GENDirectory):
        os.mkdir(GENDirectory)
    if not os.path.exists(AGGDirectory):
        os.mkdir(AGGDirectory)
        
    def processSingeConfig(regoDirectory, source, positiveValidation=True, negativeValidation=False):
        optimization = True
        attemptAmount = 3
        for regoFileName in sorted(list(os.listdir(regoDirectory))):
            if attemptAmount <= 0:
                break
            identifier = regoFileName[:-5]
            hashValue = (int(hashlib.md5(("####".join(testRule)).encode('utf-8')).hexdigest(), 16)%100000)*10000 + \
                        (int(hashlib.md5((identifier).encode('utf-8')).hexdigest(), 16)%10000)
            hashValueString = str(hashValue)
            finalResult = [resourceType, testRule, identifier, hashValue, False, False, -1, []]
            MDCResourceGroupList, GENResourceGroupList = [], []
            if source in identifier[:8]:
                print("\n\nTested identifier: ", identifier)
                jsonPath = os.path.join(jsonDirectory, identifier)
                knowledgePath = os.path.join(knowledgeDirectory, identifier)
                mappingPath = os.path.join(mappingDirectory, identifier)
                
                MDCPath = os.path.join(MDCDirectory, hashValueString+"_"+identifier)
                GENPath = os.path.join(GENDirectory, hashValueString+"_"+identifier)
                AGGPath = os.path.join(AGGDirectory, hashValueString+"_"+identifier)
                if os.path.exists(MDCPath):
                    utils.execute_cmd_imm(f"rm -rf {MDCPath}")
                if os.path.exists(GENPath):
                    utils.execute_cmd_imm(f"rm -rf {GENPath}")
                if os.path.exists(AGGPath):
                    utils.execute_cmd_imm(f"rm -rf {AGGPath}")
                if os.path.exists(knowledgePath) and os.path.exists(jsonPath) and os.path.exists(mappingPath):
                    MDCResources = None
                    MDCConfigResult = None
                    GENConfigResult = None
                    try:
                        print("\nStarting MDC SMT solving")
                        MDCResources = rego2SMTConversion(knowledgePath, mappingPath, testRule, filteredValidatedRuleList, filteredCandidateRuleList, resourceType, optimization, "MDC", iteration, MDCResources, direction, resolve)
                    except:
                        print("Something went wrong with the MDC SMT solving")
                        traceback.print_exc()
                        continue
                    if MDCResources != None and "flag" in MDCResources:
                        MDCFlag = MDCResources["flag"]
                        if MDCFlag == True:
                            print("Succeeded identifier on rule: ", identifier, testRule, hashValue) 
                            print("\nStarting MDC SMT config mutation")
                            MDCConfigResult, MDCResourceGroupList, MDCResourceSet = SMTPostprocessing.getMDCConfiguration(testRule, jsonPath, MDCPath, MDCResources, hashValue) 
                            print(f"Details of positive test case: {MDCPath}")
                        else:
                            print("Something went wrong with the MDC SMT config mutation")
                            traceback.print_exc()
                            continue
                    else:
                        print("Something went wrong with the MDC SMT results")
                        traceback.print_exc()
                        continue
                            
                    if MDCConfigResult == True:
                        
                        if "ThenAggChild" not in testRule[1] and "ThenAggParent" not in testRule[1]:
                            print("\nStarting GEN SMT solving")
                            mutationDict = rego2SMTConversion(knowledgePath, mappingPath, testRule, filteredValidatedRuleList, filteredCandidateRuleList, resourceType, optimization, "GEN", iteration, MDCResources, direction, resolve)
                            finalResult[6] = len(mutationDict["violations"])
                            if resolve == True:
                                finalResult[7] = list(mutationDict["violations"])
                            GENResult = mutationDict["satisfiability"]
                            if GENResult == True:
                                print("\nStarting GEN SMT config mutation")
                                try:
                                    GENConfigResult, GENResourceGroupList, GENResourceSet = SMTPostprocessing.getGENConfiguration(testRule, MDCPath, GENPath, mutationDict, hashValue)
                                    print(f"Details of negative test case: {GENPath}")
                                except:
                                    print(f"Something went wring during GEN SMT config mutation")
                                    continue
                            else:
                                continue
                        else:
                            print("\nStarting AGG TOPO SMT solving")
                            mutationDict = rego2SMTConversion(knowledgePath, mappingPath, testRule, filteredValidatedRuleList, filteredCandidateRuleList, resourceType, optimization, "AGGTOPO", iteration, MDCResources, direction, resolve)
                            GENResult = mutationDict["satisfiability"]
                            if GENResult == True:
                                print("\nStarting AGG ATTR SMT solving")
                                try:
                                    interDict = rego2SMTConversion(knowledgePath, mappingPath, testRule, filteredValidatedRuleList, filteredCandidateRuleList, resourceType, optimization, "AGGATTR", mutationDict, direction, resolve)
                                    finalResult[6] = len(mutationDict["violations"]) + len(interDict["violations"])
                                    if resolve == True:
                                        finalResult[7] = list(mutationDict["violations"]) + list(interDict["violations"])
                                    print("\nStarting AGG SMT config mutation")
                                    GENConfigResult, GENResourceGroupList, GENResourceSet = SMTPostprocessing.getGENConfiguration(testRule, MDCPath, GENPath, interDict, hashValue)
                                    print(f"Details of negative test case: {GENPath}")
                                except Exception as e: 
                                    print(f"Something went wring during AGG SMT config mutation", e)
                                    continue
                            else:
                                continue
                    else:
                        print("Something went wrong with the MDC SMT config mutation")
                        continue
                               
                    if original == False:
                        if direction == True and resolve == False: 
                            if finalResult[6] == -1:
                                finalResult[4] = False
                                finalResult[5] = False
                                continue
                            else:
                                finalResult[4] = True
                                finalResult[5] = True
                                print("Successfully find a case where the target rule does not overlaps, equivalent class fails!")
                                return finalResult
                    if original == True:
                        return finalResult
                    
                    if MDCConfigResult == True and positiveValidation == True:
                        attemptAmount -= 1
                        
                        tfFiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(f"{MDCPath}")) for f in fn]
                        mainFile = ""
                        for tfFile in tfFiles:
                            if ".tf.json" not in tfFile:
                                continue
                            if mainFile == "" or len(tfFile.split("/")) < len(mainFile.split("/")):
                                mainFile = tfFile
                        mainDir = "/".join(mainFile.split("/")[:-1])
                        
                        utils.execute_cmd_imm("rm -rf {mainDir}/.terraform*; rm -rf {mainDir}/terraform.tfstate")
                        #terraform_init_result = utils.execute_cmd_imm(f"cp -r ../folderFiles/.terraform* {mainDir}/.")
                        terraform_init_result = utils.execute_cmd_imm(f"cd {mainDir}; /usr/bin/timeout 150 time terraform init -input=false")
                        if terraform_init_result != "Failure":
                            print(f"MDC Terraform init succeeded: {MDCPath}!")
                        else:
                            print(f"MDC Terraform init failed: {MDCPath}!")
                            terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                            continue
                        terraform_apply_result = utils.execute_cmd_imm(f"cd {mainDir}; sudo /usr/bin/timeout 3000 time terraform apply -auto-approve")
                        flagApply = False
                        if terraform_apply_result != "Failure":
                            flagApply = True
                            print(f"MDC Terraform apply succeeded: {MDCPath}! ")
                        else:
                            flagApply = False
                            print(f"MDC Terraform apply failed: {MDCPath}!")
                            terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                            
                        localResourceSet = set()
                        try:
                            fs = open(f"{mainDir}/terraform.tfstate", "r")
                            localState = json.load(fs)
                            for localResource in localState["resources"]:
                                if localResource["mode"] == "managed":
                                    for localInstance in localResource["instances"]:
                                        localResourceSet.add((localResource["type"], localInstance["attributes"]["id"]))
                                if localResource["type"] == "azurerm_resource_group":
                                    for instance in localResource["instances"]:
                                        resourceGroupName = instance["attributes"]["name"]
                                        if "ZODIAC" not in resourceGroupName:
                                            print(f"MDC A resource group ran out of our control {MDCPath}!")
                                        terraform_destroy_result = utils.execute_cmd_imm(f"time az group delete --name {resourceGroupName} --yes --no-wait")
                                        if terraform_destroy_result != "Failure":
                                            print(f"MDC Resource group destruction succeeded: {MDCPath}!")
                                        else:
                                            terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                                            print(f"MDC Resource group destruction failed: {MDCPath}!")
                                            continue
                            for resourceGroupName in MDCResourceGroupList:
                                if "ZODIAC" not in resourceGroupName:
                                    print(f"MDC A resource group ran out of our control {MDCPath}!")
                                terraform_destroy_result = utils.execute_cmd_imm(f"time az group delete --name {resourceGroupName} --yes --no-wait")
                                if terraform_destroy_result != "Failure":
                                    print(f"MDC Resource group destruction succeeded: {MDCPath}!")
                                else:
                                    terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                                    print(f"MDC Resource group destruction failed: {MDCPath}!")
                                    continue
                        except:
                            print(f"MDC Cannot find local terraform state file {MDCPath}...")
                            
                        if flagApply == False:
                            continue
                                
                        if len(localResourceSet) != len(MDCResourceSet):
                            print(f"MDC Deployed resource amount does not match Terraform config: {MDCPath}!")
                            terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                            continue
                        else:
                            print(f"MDC Check against state file returns the correct result: {MDCPath}!")
                        
                        terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                        if terraform_purge_result != "Failure":
                            print(f"MDC Terraform purge succeeded: {MDCPath}! ")
                        else:
                            print(f"MDC Terraform purge failed: {MDCPath}!")
                            continue
                        finalResult[4] = True
                    elif positiveValidation == False:
                        finalResult[4] = None
                    else:
                        print(f"Try another MDC configuration {MDCPath}!")
                        continue
                    
                    if GENConfigResult == True and negativeValidation == True:
                        tfFiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(f"{GENPath}")) for f in fn]
                        mainFile = ""
                        for tfFile in tfFiles:
                            if ".tf.json" not in tfFile:
                                continue
                            if mainFile == "" or len(tfFile.split("/")) < len(mainFile.split("/")):
                                mainFile = tfFile
                        mainDir = "/".join(mainFile.split("/")[:-1])
                        
                        utils.execute_cmd_imm("rm -rf {mainDir}/.terraform*; rm -rf {mainDir}/terraform.tfstate")
                        #terraform_init_result = utils.execute_cmd_imm(f"cp -r ../folderFiles/.terraform* {mainDir}/.")
                        terraform_init_result = utils.execute_cmd_imm(f"cd {mainDir}; /usr/bin/timeout 150 time terraform init -input=false")
                        if terraform_init_result != "Failure":
                            print(f"GEN Terraform init succeeded: {GENPath}!")
                        else:
                            print(f"GEN Terraform init failed: {GENPath}!")
                            terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                            continue
                        
                        terraform_plan_result = utils.execute_cmd_imm(f'cd {mainDir}; sudo /usr/bin/timeout 3000 time terraform plan -out=output.tfplan')
                        if terraform_plan_result != "Failure":
                            print(f"GEN Terraform plan succeeded: {GENPath}! ")
                        else:
                            print(f"GEN Terraform plan failed: {GENPath}!")
                            terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                            continue
                        
                        terraform_apply_result = utils.execute_cmd_imm(f'cd {mainDir}; sudo /usr/bin/timeout 3000 time terraform apply -auto-approve output.tfplan')
                        flagApply = False
                        if terraform_apply_result != "Failure":
                            flagApply = True
                            print(f"GEN Terraform apply succeeded: {GENPath}! ")
                        else:
                            flagApply = False
                            print(f"GEN Terraform apply failed: {GENPath}!")
                            terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                            
                        localResourceSet = set()
                        try:
                            fs = open(f"{mainDir}/terraform.tfstate", "r")
                            localState = json.load(fs)
                            for localResource in localState["resources"]:
                                if localResource["mode"] == "managed":
                                    for localInstance in localResource["instances"]:
                                        localResourceSet.add((localResource["type"], localInstance["attributes"]["id"]))
                                if localResource["type"] == "azurerm_resource_group":
                                    for instance in localResource["instances"]:
                                        resourceGroupName = instance["attributes"]["name"]
                                        if "ZODIAC" not in resourceGroupName:
                                            print(f"GEN A resource group ran out of our control {GENPath}!")
                                        terraform_destroy_result = utils.execute_cmd_imm(f"time az group delete --name {resourceGroupName} --yes --no-wait")
                                        if terraform_destroy_result != "Failure":
                                            print(f"GEN Resource group destruction succeeded: {GENPath}!")
                                        else:
                                            terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                                            print(f"GEN Resource group destruction failed: {GENPath}!")
                                            continue
                            for resourceGroupName in GENResourceGroupList:
                                if "ZODIAC" not in resourceGroupName:
                                    print(f"GEN A resource group ran out of our control {GENPath}!")
                                terraform_destroy_result = utils.execute_cmd_imm(f"time az group delete --name {resourceGroupName} --yes --no-wait")
                                if terraform_destroy_result != "Failure":
                                    print(f"GEN Resource group destruction succeeded: {GENPath}!")
                                else:
                                    terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                                    print(f"GEN Resource group destruction failed: {GENPath}!")
                                    continue
                        except:
                            print(f"GEN Cannot find local terraform state file {GENPath}...")
                        
                        terraform_purge_result = utils.execute_cmd_imm(f"cd {mainDir}; rm -rf .terraform*")
                        if terraform_purge_result != "Failure":
                            print(f"GEN Terraform purge succeeded: {GENPath}! ")
                        else:
                            print(f"GEN Terraform purge failed: {GENPath}!")
                            continue
                        
                        if flagApply == True:
                            if len(localResourceSet) != len(GENResourceSet):
                                print(f"GEN Deployed resource amount does not match Terraform config: {GENPath}!")
                                flagApply = False
                            else:
                                print(f"GEN Check against state file returns the correct result: {GENPath}!")
                        
                        finalResult[5] = flagApply
                        if flagApply == True:
                            validity = False
                        else:
                            validity = True
                        print(f"Successfully validate a rule: {testRule}, Deployment result was {flagApply}, i.e., the check is potentially {validity}, {finalResult[6]}")
                        return finalResult
                    elif positiveValidation == False:
                        finalResult[5] = None
                        return finalResult
                    else:
                        print(f"Try another GEN configuration! {GENPath}")
                        continue
                else:
                    print("The current identifier does not have required context information")
        return finalResult
    
    positiveValidation = True
    negativeValidation = True
    
    try:
        finalResult = processSingeConfig(regoDirectory, "tflint", positiveValidation, negativeValidation)
        violationCount = finalResult[6]
        deployResult = finalResult[5]
        findProgress1 = finalResult[4]
        hashValue = finalResult[3]
        identifier = finalResult[2]
        if findProgress1 and resolve == False:
            details = [testRule, hashValue, identifier, "usageExamples", deployResult, violationCount]
            fr = open(f"{validationDirectory}/rule_{hashValueTemp}.json", "w")
            json.dump(details, fr, sort_keys = True, indent = 4)
            fr.close()
            return result, "usageExamples"
        elif findProgress1 and resolve == True:
            conflictList = finalResult[7]
            details = [testRule, hashValue, identifier, "usageExamples", deployResult, violationCount, conflictList]
            fr = open(f"{validationDirectory}/rule_{hashValueTemp}.json", "w")
            json.dump(details, fr, sort_keys = True, indent = 4)
            fr.close()
            return result, "usageExamples"
    except:
        print("Something went wrong when trying to retrieve results from usageExamples")
        traceback.print_exc()
    
    try:
        finalResult = processSingeConfig(regoDirectory, "provider", positiveValidation, negativeValidation)
        violationCount = finalResult[6]
        deployResult = finalResult[5]
        findProgress2 = finalResult[4]
        hashValue = finalResult[3]
        identifier = finalResult[2]
        if findProgress2 and resolve == False:
            details = [testRule, hashValue, identifier, "examples", deployResult, violationCount]
            fr = open(f"{validationDirectory}/rule_{hashValueTemp}.json", "w")
            json.dump(details, fr, sort_keys = True, indent = 4)
            fr.close()
            return result, "examples"
        elif findProgress2 and resolve == True:
            conflictList = finalResult[7]
            details = [testRule, hashValue, identifier, "examples", deployResult, violationCount, conflictList]
            fr = open(f"{validationDirectory}/rule_{hashValueTemp}.json", "w")
            json.dump(details, fr, sort_keys = True, indent = 4)
            fr.close()
            return result, "examples"
    except:
        print("Something went wrong when trying to retrieve results from examples")
        traceback.print_exc()
    
    try:
        finalResult = processSingeConfig(regoDirectory, "folder", positiveValidation, negativeValidation)
        violationCount = finalResult[6]
        deployResult = finalResult[5]
        findProgress3 = finalResult[4]
        hashValue = finalResult[3]
        identifier = finalResult[2]
        if findProgress3 and resolve == False:
            details = [testRule, hashValue, identifier, "folders", deployResult, violationCount]
            fr = open(f"{validationDirectory}/rule_{hashValueTemp}.json", "w")
            json.dump(details, fr, sort_keys = True, indent = 4)
            fr.close()
            return result, "folderFiles"
        elif findProgress3 and resolve == True:
            conflictList = finalResult[7]
            details = [testRule, hashValue, identifier, "folderFiles", deployResult, violationCount, conflictList]
            fr = open(f"{validationDirectory}/rule_{hashValueTemp}.json", "w")
            json.dump(details, fr, sort_keys = True, indent = 4)
            fr.close()
            return result, "folderFiles"
    except:
        print("Something went wrong when trying to retrieve results from folderFiles")
        traceback.print_exc()
    
    print(f"failed candidate rule: {result}")
    return result, "positive test case failure"

### Validation process for an entire iteration-direction (e.g. first true positive validation pass)
def validationProcess(direction, resolve, interpolation, controlIndex):
    if not os.path.exists(f"../testFiles/"):
        os.mkdir(f"../testFiles/")
    
    if interpolation == True:
        interpolationDataRawList = json.load(open(f"../testFiles/interpolationCandidate.json", "r"))
        interpolationDataList = []
        for resourceType, rule, ruleString in interpolationDataRawList:
            interpolationDataList.append([resourceType, rule])
        truthDataList = json.load(open(f"../testFiles/interValidatedFile{controlIndex}.json", "r"))
        tempValue = controlIndex-1
        if tempValue == 0:
            ruleDataList = interpolationDataList[:]
        else:
            ruleDataList = json.load(open(f"../testFiles/interCandidateFile{tempValue}.json", "r"))
        for index in range(0, len(ruleDataList)):
            targetRuleDetail = ruleDataList[index][1].split(",")
            if "AggChild" in targetRuleDetail[1] and targetRuleDetail[-2].split(" ")[-1] not in ["1", "2", "4", "8", "16"]:
                print("Cannot handle this aggregation rule for now!")
                continue
            elif "AggParent" in targetRuleDetail[1] and targetRuleDetail[-1].split(" ")[-1] not in ["1", "2", "4", "8", "16"]:
                print("Cannot handle this aggregation rule for now!")
                continue
            elif "CIDRRange" in targetRuleDetail[1] and targetRuleDetail[-1].split(" ")[-1] == "32":
                print("Cannot handle this aggregation rule for now!")
                continue
            print("Examine candidate: ", ruleDataList[index])
            arglists.append([[ruleDataList[index][0], 'I', ruleDataList[index][1]], truthDataList, ruleDataList, [], False, controlIndex, True, True, True])
    elif direction == True:
        ruleDataList = json.load(open(f"../testFiles/completeFile{controlIndex}.json", "r"))
        tempValue = controlIndex-1
        interpolationDataList = []
        truthDataList = json.load(open(f"../testFiles/validatedFile{tempValue}.json", "r"))
        for index in range(0, len(ruleDataList)):
            print("Examine candidate: ", ruleDataList[index])
            #coreValidationPipeline([ruleDataList[index][0], 'M', ruleDataList[index][1]], truthDataList, ruleDataList, interpolationDataList, False, controlIndex, direction, resolve)
            arglists.append([[ruleDataList[index][0], 'M', ruleDataList[index][1]], truthDataList, ruleDataList, interpolationDataList, False, controlIndex, direction, resolve])
    else:
        interpolationDataList = []
        ruleDataList = json.load(open(f"../testFiles/candidateFile{controlIndex}.json", "r"))
        truthDataList = json.load(open(f"../testFiles/validatedFile{controlIndex}.json", "r"))
        for index in range(0, len(ruleDataList)):
            print("Examine candidate: ", ruleDataList[index])
            arglists.append([[ruleDataList[index][0], 'M', ruleDataList[index][1]], truthDataList, ruleDataList, interpolationDataList, False, controlIndex, direction, resolve])
            #coreValidationPipeline([ruleDataList[index][0], 'M', ruleDataList[index][1]], truthDataList, ruleDataList, interpolationDataList, False, controlIndex, direction, resolve)
    pool = multiprocessing.Pool(processes=12)
    for arglist in arglists:
        pool.apply_async(coreValidationPipeline, args=arglist)
    pool.close()
    pool.join()
    
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--control_index", help="current iteration identifier")
    parser.add_argument("--direction", help="true positive validation or false positive removal. This will override resolve argument")
    parser.add_argument("--resolve", help="whether to resolve indistinct groups", default = "True")
    parser.add_argument("--interpolation", help="dealing with interpolation rules. This will override resolve and direction argument")
    args = parser.parse_args()
    return args

### Usage example: sudo time python3 -u SMTPipeline.py --control_index 0 --direction False --interpolation False > output1 2>output2
### Usage example: sudo time python3 -u SMTPipeline.py --control_index 1 --direction True --interpolation False > output3 2>output4
### Usage example: sudo time python3 -u SMTPipeline.py --control_index 1 --direction True --interpolation True > output5 2>output6
if __name__ == "__main__":
    arglists = []
    args = parse_args()
    controlIndex = int(args.control_index)
    if str(args.direction) == "True":
        direction = True
    else:
        direction = False
    if str(args.resolve) == "True":
        resolve = True
    else:
        resolve = False
    if str(args.interpolation) == "True":
        interpolation = True
    else:
        interpolation = False
    validationProcess(direction, resolve, interpolation, controlIndex)
