### Main entry for source code transformation. Both positive test case pruning and
### negative test case mutation is defined here.
import sys
import os
sys.path.insert(0, '..')
sys.path.insert(0, '../ruleTemplateInstantiation')
import utils.utils as utils
import json
from utils.utils import *
from collections import defaultdict
import copy
import traceback

### mutate attribute values in the json format configuration (replace original with compiled)
def concretizeAttributes(resourceJsonData, plan, ExistingResourceSet):
    for resourceList in resourceJsonData["resource"]:
        for resourceType in resourceList:
            for resourceName in resourceList[resourceType]:
                for resourceBlock in plan:
                    if resourceBlock["address"] == resourceType + "." + resourceName:
                        for resourceAttribute in list(resourceList[resourceType][resourceName].keys()):
                            if resourceAttribute == "provisioner":
                                del(resourceList[resourceType][resourceName][resourceAttribute])
                            if resourceAttribute not in resourceBlock["values"]:
                                continue
                            resourceValue = resourceList[resourceType][resourceName][resourceAttribute]
                            if type(resourceValue) == str and "${" in resourceValue:
                            
                                flagChange = True
                                # for depResource in ExistingResourceSet:
                                #     if depResource in resourceValue:
                                #         flagChange = False
                                if "name" in resourceAttribute:
                                    flagChange = False
                                if flagChange == False:
                                    continue
                                resourceList[resourceType][resourceName][resourceAttribute] = resourceBlock["values"][resourceAttribute]
                            elif type(resourceValue) == list and type(resourceBlock["values"][resourceAttribute]) == list:
                                for index in range(min(len(resourceValue),len(resourceBlock["values"][resourceAttribute]))):
                                    if type(resourceList[resourceType][resourceName][resourceAttribute][index]) != dict:
                                        continue
                                    for resourceSubAttribute in resourceList[resourceType][resourceName][resourceAttribute][index]:
                                        flagChange = True
                                        if resourceSubAttribute not in resourceBlock["values"][resourceAttribute][index]:
                                            flagChange = False
                                            continue
                                        resourceSubValue = resourceList[resourceType][resourceName][resourceAttribute][index][resourceSubAttribute]
                                        if type(resourceSubValue) == str and "${" in resourceSubValue:
                                            # for depResource in ExistingResourceSet:
                                            #     if depResource in resourceValue:
                                            #         flagChange = False
                                            if "name" in resourceAttribute:
                                                flagChange = False
                                            if flagChange == False:
                                                continue
                                            resourceList[resourceType][resourceName][resourceAttribute][index][resourceSubAttribute] = resourceBlock["values"][resourceAttribute][index][resourceSubAttribute]
                                                   
### Given the original json congiuration and result of MDC purpsoe SMT solving, retrieve MDC configuration.
def getMDCConfiguration(testRule, jsonInputDirName, jsonOutputDirName, MDCResources, resourceGroupStartId):
    try:
        MDCResourceSet = set()
        if not os.path.exists(jsonOutputDirName):
            os.mkdir(jsonOutputDirName)
        utils.execute_cmd_imm(f"cp -r {jsonInputDirName}/* {jsonOutputDirName}")
        for resourceName in MDCResources["MDC"]:
            for ancestorResource in MDCResources["inclusiveAncestorDict"][resourceName]:
                MDCResourceSet.add(ancestorResource)
            
        plan = MDCResources["plan"] + MDCResources["planOriginal"]
        print("MDCResourceSet: ", MDCResourceSet)
        tfFiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(f"{jsonOutputDirName}")) for f in fn]
        
        resourceGroupList = []
        resourceGroupId = resourceGroupStartId
        storageAccountId = resourceGroupStartId
        resourceGroupNum = 0
        for tfFile in tfFiles:
            if ".tf.json" not in tfFile:
                continue
            ### Basic MDC processing, rename resource groups and storage account, remove non-MDC resources
            resourceJsonData = json.load(open(f"{tfFile}", "r"))
            ### Just remove all output blocks given that we don not support modules anyway 
            if "output" in resourceJsonData:
                del(resourceJsonData["output"])
                
            ### remove data blocks based on their dependencies
            if "data" in resourceJsonData:
                dataDataCopy = copy.deepcopy(resourceJsonData["data"])
                resourceJsonData["data"] = []
                for dataList in dataDataCopy:
                    flagDataChangeSum = 0
                    for dataType in dataList:
                        for dataName in dataList[dataType]:
                            print("dataName:", dataName)
                            for dataAttribute in dataList[dataType][dataName]:
                                dataValue = dataList[dataType][dataName][dataAttribute]
                                if type(dataValue) == str and "${" in dataValue:
                                    flagDataChange = True
                                    for depResource in MDCResourceSet:
                                        if depResource in dataValue:
                                            flagDataChange = False
                                    if flagDataChange == True:
                                        flagDataChangeSum += 1
                                elif type(dataValue) == list:
                                    for index in range(len(dataValue)):
                                        if type(dataList[dataType][dataName][dataAttribute][index]) != dict:
                                            continue
                                        for dataSubAttribute in dataList[dataType][dataName][dataAttribute][index]:
                                            dataSubValue = dataList[dataType][dataName][dataAttribute][index][dataSubAttribute]
                                            
                                            if type(dataSubValue) == str and "${" in dataSubValue:
                                                flagDataChange = True
                                                for depResource in MDCResourceSet:
                                                    if depResource in dataValue:
                                                        flagDataChange = False
                                                if flagDataChange == True:
                                                    flagDataChangeSum += 1
                    if flagDataChangeSum == 0:
                        resourceJsonData["data"].append(dataList)   
                if len(resourceJsonData["data"]) == 0:
                    del(resourceJsonData["data"])  
            if "resource" not in resourceJsonData:
                with open(f"{tfFile}", 'w') as f:
                    json.dump(resourceJsonData, f, indent = 4)
                continue

            resourceDataCopy = copy.deepcopy(resourceJsonData["resource"])
            resourceJsonData["resource"] = []
            for resourceList in resourceDataCopy:
                for resourceType in list(resourceList.keys()):
                    for resourceName in list(resourceList[resourceType].keys()):
                        if resourceType+"."+resourceName not in MDCResourceSet:
                            del(resourceList[resourceType][resourceName])
                        elif resourceType == "azurerm_resource_group":
                            for resourceAttribute in resourceList[resourceType][resourceName]:
                                if resourceAttribute in ["name"]:
                                    resourceList[resourceType][resourceName][resourceAttribute] = f"ZODIAC-MDC-{resourceGroupId}"
                                    resourceGroupList.append(f"ZODIAC-MDC-{resourceGroupId}")
                                    resourceGroupId += 1
                                    resourceGroupNum += 1
                        elif resourceType in ["azurerm_storage_account", "azurerm_linux_web_app", "azurerm_mssql_server"]:
                            ### These resources require globally unique names
                            for resourceAttribute in resourceList[resourceType][resourceName]:
                                if resourceAttribute in ["name"]:
                                    resourceList[resourceType][resourceName][resourceAttribute] = f"zodiacymdc{storageAccountId}"
                                    storageAccountId += 1
                        
                    if len(resourceList[resourceType]) == 0:
                        del(resourceList[resourceType])
                if resourceList:
                    resourceJsonData["resource"].append(resourceList)  
            
            concretizeAttributes(resourceJsonData, plan, MDCResourceSet)
                                                    
            if len(resourceJsonData["resource"]) == 0:
                del(resourceJsonData["resource"])
                         
            with open(f"{tfFile}", 'w') as f:
                json.dump(resourceJsonData, f, indent = 4) 
        print(f"Count resource group amount: {resourceGroupNum}...") 
        if resourceGroupNum  > 2:
            return False, resourceGroupList, MDCResourceSet
        return True, resourceGroupList, MDCResourceSet
    except Exception as e:
        print(f"MDC json configuration construction failed: {e}!")
        traceback.print_exc()
        return False, [], set()

def getGENConfiguration(testRule, jsonInputDirName, jsonOutputDirName, mutationDict, resourceGroupStartId):
    try:
        if not os.path.exists(jsonOutputDirName):
            os.mkdir(jsonOutputDirName)
        GENResourceSet = set()
        #utils.execute_cmd_imm(f"rm -rf {jsonOutputDirName}/*")
        utils.execute_cmd_imm(f"cp -r {jsonInputDirName}/* {jsonOutputDirName}")
        repoStringListView = json.load(open("../regoFiles/repoStringListView.json", "r"))
        globalTypeFile = f"../folderFiles/globalType.json"
        globalTypeDict = json.load(open(f"{globalTypeFile}", "r"))
        resourceGroupList = []
        ### Obtain all used virtual resources from the mutated dependency list.
        usedVirtualResources = set()
        for outputPort, inputPort in mutationDict["dependency"]:
            inputResourceType = inputPort.split(".")[0]
            inputResourceName = inputPort.split(".")[1]
            outputResourceType = outputPort.split(".")[0]
            outputResourceName = outputPort.split(".")[1]
            if "ZODIAC" in inputResourceName:
                usedVirtualResources.add(inputResourceType + "." + inputResourceName)
            if "ZODIAC" in outputResourceName:
                usedVirtualResources.add(outputResourceType + "." + outputResourceName)
        print(f"usedVirtualResources: {usedVirtualResources}")
        
        ### A set of variables that are useful for the following config mutation procedure.
        new2oldMapping = mutationDict["mapping"]
        additionalResource = mutationDict["additional"]
        resourceDependencyView = mutationDict["dependencyView"]
        plan = mutationDict["plan"] + mutationDict["planOriginal"]
        ExistingResourceSet = set()
        resourceDetailDict = defaultdict(list)
        ignoredResourceSet = mutationDict["ignoredResourceSet"]
        ### Obtain mapping between existing resources and newly added resources.
        for newAddr in new2oldMapping:
            oldAddr = new2oldMapping[newAddr]
            ExistingResourceSet.add(newAddr)
            resourceDetailDict[oldAddr].append(newAddr)
        for oldAddr in resourceDetailDict:
            if oldAddr not in resourceDetailDict[oldAddr]:
                resourceDetailDict[oldAddr].append(oldAddr)
            
        print(f"resourceDetailDict: {resourceDetailDict}")
        print(f"ignoredResourceSet: {ignoredResourceSet}")
        
        
        tfFiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(f"{jsonOutputDirName}")) for f in fn]
        resourceGroupId = resourceGroupStartId + 100
        storageAccountId = resourceGroupStartId + 100
        virtualResourceId = resourceGroupStartId + 200
        
        tfFileIndex = 0
        for tfFile in tfFiles:
            if ".tf.json" not in tfFile:
                continue
            resourceJsonData = json.load(open(f"{tfFile}", "r"))
            if "output" in resourceJsonData:
                del(resourceJsonData["output"])
            if "resource" not in resourceJsonData:
                with open(f"{tfFile}", 'w') as f:
                    json.dump(resourceJsonData, f, indent = 4)
                continue
            tfFileIndex += 1
            
            ### initiate additional resources needed by negation and exclusive operators
            if tfFileIndex == 1:
                print("Additional resources: ", additionalResource)
                for resourceName in additionalResource:
                    if resourceName not in usedVirtualResources and "ZODIAC" in resourceName:
                        continue
                    newResourceList = dict()
                    resourceType = resourceName.split(".")[0]
                    newResourceList[resourceType] = dict()
                    newResourceName = resourceName.split(".")[-1]
                    newResourceList[resourceType][newResourceName] = additionalResource[resourceName][1]
                    addFlag = True
                    for tempResourceList in resourceJsonData["resource"]:
                        if resourceType in tempResourceList and newResourceName in tempResourceList[resourceType]:
                            addFlag = False
                    if addFlag == True:
                        resourceJsonData["resource"].append(newResourceList)
                    #plan.append(additionalResource[resourceName][1])
            
            resourceDataCopy = copy.deepcopy(resourceJsonData["resource"])
            resourceJsonData["resource"] = []        
            ### initiate virtual resources and rename resource groups(i.e. top level entities)
            for resourceList in resourceDataCopy:
                for resourceType in list(resourceList.keys()):
                    for resourceName in list(resourceList[resourceType].keys()):
                        resourceAddress = resourceType+"."+resourceName
                        if resourceAddress in resourceDetailDict:
                            for newResourceAddress in resourceDetailDict[resourceAddress]:
                                if newResourceAddress in ignoredResourceSet:
                                    continue
                                if newResourceAddress != resourceAddress and newResourceAddress not in usedVirtualResources:
                                    continue
                                newResourceBlock = copy.deepcopy(resourceList[resourceType][resourceName])
                                newResourceList = dict()
                                newResourceList[resourceType] = dict()
                                newResourceName = newResourceAddress.split(".")[-1]
                                newResourceList[resourceType][newResourceName] = newResourceBlock
                                
                                if resourceType == "azurerm_resource_group":
                                    for resourceAttribute in newResourceList[resourceType][newResourceName]:
                                        if resourceAttribute in ["name"]:
                                            newResourceList[resourceType][newResourceName][resourceAttribute] = f"ZODIAC-GEN-{resourceGroupId}"
                                            resourceGroupList.append(f"ZODIAC-GEN-{resourceGroupId}")
                                            resourceGroupId += 1
                                elif resourceType in ["azurerm_storage_account", "azurerm_linux_web_app", "azurerm_mssql_server"]:
                                    ### These resources require globally unique names
                                    for resourceAttribute in newResourceList[resourceType][newResourceName]:
                                        if resourceAttribute in ["name"]:
                                            newResourceList[resourceType][newResourceName][resourceAttribute] = f"zodiacgen{storageAccountId}"
                                            storageAccountId += 1
                                else:
                                    for resourceAttribute in newResourceList[resourceType][newResourceName]:
                                        if resourceAttribute in ["name"]:
                                            newResourceList[resourceType][newResourceName][resourceAttribute] = f"zodiacvir{virtualResourceId}"
                                            virtualResourceId += 1
                                resourceJsonData["resource"].append(newResourceList)
                        else:
                            if resourceAddress in ignoredResourceSet:
                                continue
                            if resourceType == "azurerm_resource_group":
                                if "name" in resourceList[resourceType][resourceName]:
                                    resourceList[resourceType][resourceName]["name"] = f"ZODIAC-GEN-{resourceGroupId}"
                                    resourceGroupList.append(f"ZODIAC-GEN-{resourceGroupId}")
                                    resourceGroupId += 1
                            elif resourceType in ["azurerm_storage_account", "azurerm_linux_web_app", "azurerm_mssql_server"]:
                                ### These resources require globally unique names
                                if "name" in resourceList[resourceType][resourceName]:
                                    resourceList[resourceType][resourceName]["name"] = f"zodiacgen{storageAccountId}"
                                    storageAccountId += 1
                            resourceJsonData["resource"].append(resourceList)
                            
            concretizeAttributes(resourceJsonData, plan, ExistingResourceSet)
            
            ### mutate topology edges in the json format configuration   
            cleansedSet = set() 
            for outputPort, inputPort in mutationDict["dependency"]:
                inputResourceType = inputPort.split(".")[0]
                inputResourceName = inputPort.split(".")[1]
                inputResourceAttributeList = inputPort.split(".")[2:]
                for resourceList in resourceJsonData["resource"]:
                    for resourceType in resourceList:
                        for resourceName in resourceList[resourceType]:
                            if  inputResourceType == resourceType and inputResourceName == resourceName:
                                resourceAttribute = inputResourceAttributeList[0]
                                if len(inputResourceAttributeList) == 1:
                                    if resourceAttribute not in resourceList[resourceType][resourceName]:
                                        resourceList[resourceType][resourceName][resourceAttribute] = None
                                    resourceValue = resourceList[resourceType][resourceName][resourceAttribute]
                                elif len(inputResourceAttributeList) == 3:
                                    attributeIndex = int(inputResourceAttributeList[1])
                                    resourceSubAttribute = inputResourceAttributeList[2]
                                    ### TODO: How to handle cases where the whole block does not exist in advance?
                                    if resourceAttribute not in resourceList[resourceType][resourceName]:
                                        continue
                                    while len(resourceList[resourceType][resourceName][resourceAttribute]) <= attributeIndex:
                                        resourceList[resourceType][resourceName][resourceAttribute].append(copy.deepcopy(resourceList[resourceType][resourceName][resourceAttribute][-1]))
                                    if resourceSubAttribute not in resourceList[resourceType][resourceName][resourceAttribute][attributeIndex]:
                                        resourceList[resourceType][resourceName][resourceAttribute][attributeIndex][resourceSubAttribute] = None
                                    resourceValue = resourceList[resourceType][resourceName][resourceAttribute][attributeIndex][resourceSubAttribute]
                                else:
                                    continue
                                if type(resourceValue) == list:
                                    if "ZODIAC" in resourceName and inputPort not in cleansedSet:
                                        cleansedSet.add(inputPort)
                                        resourceValue = []
                                    resourceValue.append("${" + outputPort + "}") 
                                else:
                                    resourceValue = "${" + outputPort + "}" 
                                if len(inputResourceAttributeList) == 1:
                                    resourceList[resourceType][resourceName][resourceAttribute] = resourceValue
                                elif len(inputResourceAttributeList) == 3: 
                                    resourceList[resourceType][resourceName][resourceAttribute][attributeIndex][resourceSubAttribute] = resourceValue
            
            ### remove topo input port that are not in use.
            for resourceList in resourceJsonData["resource"]:
                for resourceType in resourceList:
                    for resourceName in resourceList[resourceType]:
                        GENResourceSet.add(resourceType+"."+resourceName)
                        if "ZODIAC" in resourceName:
                            for _, _, ref1, _ in resourceDependencyView[resourceType]:
                                inputPortName = resourceType + "." + resourceName + "." + ref1
                                initFlag = False
                                for _, r in mutationDict["dependency"]:
                                    if r == inputPortName:
                                        initFlag = True
                                inputResourceAttributeList = ref1.split(".")
                                if initFlag == False:
                                    if len(inputResourceAttributeList) == 1:
                                        resourceAttribute = inputResourceAttributeList[0]
                                        if resourceAttribute in resourceList[resourceType][resourceName]:
                                            del(resourceList[resourceType][resourceName][resourceAttribute])
                                    elif len(inputResourceAttributeList) == 3:
                                        resourceAttribute = inputResourceAttributeList[0]
                                        attributeIndex = int(inputResourceAttributeList[1])
                                        resourceSubAttribute = inputResourceAttributeList[2]
                                        if resourceAttribute not in resourceList[resourceType][resourceName]:
                                            continue
                                        if len(resourceList[resourceType][resourceName][resourceAttribute]) <= attributeIndex:
                                            continue
                                        if resourceSubAttribute in resourceList[resourceType][resourceName][resourceAttribute][attributeIndex]:
                                            del(resourceList[resourceType][resourceName][resourceAttribute][attributeIndex][resourceSubAttribute])
                                else:
                                    ### If not the first elelment in set, delete regardless of other reasons.
                                    if len(inputResourceAttributeList) == 3:
                                        resourceAttribute = inputResourceAttributeList[0]
                                        attributeIndex = int(inputResourceAttributeList[1])
                                        resourceSubAttribute = inputResourceAttributeList[2]
                                        if resourceAttribute not in resourceList[resourceType][resourceName]:
                                            continue
                                        if len(resourceList[resourceType][resourceName][resourceAttribute]) <= attributeIndex:
                                            continue
                                        if resourceSubAttribute in resourceList[resourceType][resourceName][resourceAttribute][attributeIndex]:
                                            if "${azurerm" in resourceList[resourceType][resourceName][resourceAttribute][attributeIndex][resourceSubAttribute]:
                                                resourceList[resourceType][resourceName][resourceAttribute] = resourceList[resourceType][resourceName][resourceAttribute][:1]
            
            ###  mutate attribute values in the json format configuration (replace original with mutated)                   
            for attributeKey, newValue, oldValue, attributeIndex in mutationDict["attribute"]:
                originalAttributeIndex = attributeIndex
                print(attributeKey, newValue, oldValue)
                targetResourceType = attributeKey.split(".")[0]
                targetResourceName = attributeKey.split(".")[1]
                targetResourceAttributeList = attributeKey.split(".")[2:]
                for resourceList in resourceJsonData["resource"]:
                    for resourceType in resourceList:
                        for resourceName in resourceList[resourceType]:
                            if  targetResourceType == resourceType and targetResourceName == resourceName:
                                resourceAttribute = targetResourceAttributeList[0]
                                if len(targetResourceAttributeList) == 1:
                                    if resourceAttribute not in resourceList[resourceType][resourceName]:
                                        resourceList[resourceType][resourceName][resourceAttribute] = None
                                    resourceValue = resourceList[resourceType][resourceName][resourceAttribute]
                                elif len(targetResourceAttributeList) == 2:
                                    #attributeIndex = 0
                                    resourceSubAttribute = targetResourceAttributeList[1]
                                    ### TODO: How to handle cases where the whole block does not exist in advance?
                                    if resourceAttribute not in resourceList[resourceType][resourceName]:
                                        continue
                                    if newValue in ["Absence", "Existence"] or len(resourceList[resourceType][resourceName][resourceAttribute]) == 1: 
                                        if resourceSubAttribute not in resourceList[resourceType][resourceName][resourceAttribute][attributeIndex]:
                                            resourceList[resourceType][resourceName][resourceAttribute][attributeIndex][resourceSubAttribute] = None
                                    else:
                                        for tempIndex in range(len(resourceList[resourceType][resourceName][resourceAttribute])):
                                            if resourceSubAttribute in resourceList[resourceType][resourceName][resourceAttribute][tempIndex]:
                                                if oldValue == "true" or oldValue == "True":
                                                    tempOldValue = True
                                                elif oldValue == "false" or oldValue == "False":
                                                    tempOldValue = False
                                                elif oldValue == "":
                                                    tempOldValue = None
                                                elif oldValue.isnumeric():
                                                    tempOldValue = int(oldValue)
                                                else:
                                                    tempOldValue = oldValue
                                                if resourceList[resourceType][resourceName][resourceAttribute][tempIndex][resourceSubAttribute] == tempOldValue:
                                                    attributeIndex = tempIndex
                                                    if originalAttributeIndex == 0:
                                                        break
                                    resourceValue = resourceList[resourceType][resourceName][resourceAttribute][attributeIndex][resourceSubAttribute]
                                
                                if newValue == "Absence":
                                    flagFound = False
                                    for _, jsonBlock, _ in globalTypeDict[resourceType]:
                                        if len(targetResourceAttributeList) == 1:
                                            if resourceAttribute in jsonBlock:
                                                if not jsonBlock[resourceAttribute] or jsonBlock[resourceAttribute] == None:
                                                    resourceList[resourceType][resourceName][resourceAttribute] = jsonBlock[resourceAttribute] 
                                                    flagFound = True
                                                    break
                                        elif len(targetResourceAttributeList) == 2:
                                            if resourceAttribute in jsonBlock and len(jsonBlock[resourceAttribute]) >= 1 and resourceSubAttribute in jsonBlock[resourceAttribute][0]:
                                                if not jsonBlock[resourceAttribute][0][resourceSubAttribute] or jsonBlock[resourceAttribute][0][resourceSubAttribute] == None:
                                                    resourceList[resourceType][resourceName][resourceAttribute][0][resourceSubAttribute] = jsonBlock[resourceAttribute][0][resourceSubAttribute]
                                                    flagFound = True
                                                    break
                                    if flagFound == False:
                                        if len(targetResourceAttributeList) == 1:
                                            del(resourceList[resourceType][resourceName][resourceAttribute])
                                        elif len(targetResourceAttributeList) == 2:
                                            del(resourceList[resourceType][resourceName][resourceAttribute][0][resourceSubAttribute])
                                elif newValue == "Existence":
                                    flagFound = False
                                    if len(targetResourceAttributeList) == 1:
                                        for _, jsonBlock, _ in globalTypeDict[resourceType]:
                                            if resourceAttribute in jsonBlock:
                                                if jsonBlock[resourceAttribute] and jsonBlock[resourceAttribute] != None:
                                                    resourceList[resourceType][resourceName][resourceAttribute] = jsonBlock[resourceAttribute] 
                                                    flagFound = True
                                                    break
                                    elif len(targetResourceAttributeList) == 2:
                                        try:
                                            resourceList[resourceType][resourceName][resourceAttribute][0][resourceSubAttribute] = repoStringListView[resourceType][".".join(targetResourceAttributeList)][0]
                                            flagFound = True
                                        except:
                                            flagFound = False
                                    if flagFound == False:
                                        mappingDirectory = f"../folderFiles/folders_{resourceType}_mapping" 
                                        if not os.path.exists(mappingDirectory):
                                            break
                                        for mappingFileName in sorted(list(os.listdir(mappingDirectory))):
                                            mappingPath = os.path.join(mappingDirectory, mappingFileName)
                                            mappingFiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(f"{mappingPath}")) for f in fn]
                                            mainFile = ""
                                            for mappingFile in mappingFiles:
                                                if "type.json" in mappingFile:
                                                    mainFile = mappingFile

                                            if mainFile == "":
                                                continue
                                            else:
                                                localTypeDict = json.load(open(f"{mainFile}", "r"))
                                                try:
                                                    if resourceType in localTypeDict:
                                                        for tempItem in localTypeDict[resourceType]:
                                                            jsonBlock =  tempItem[1]
                                                            if resourceAttribute in jsonBlock:
                                                                if len(targetResourceAttributeList) == 1:
                                                                    if jsonBlock[resourceAttribute] and jsonBlock[resourceAttribute] != None:
                                                                        print("Existence value:", jsonBlock[resourceAttribute])
                                                                        resourceList[resourceType][resourceName][resourceAttribute] = jsonBlock[resourceAttribute]
                                                                        flagFound = True
                                                                        break
                                                                elif len(targetResourceAttributeList) == 2:
                                                                    if resourceAttribute in jsonBlock and len(jsonBlock[resourceAttribute]) >= 1 and resourceSubAttribute in jsonBlock[resourceAttribute][0]:
                                                                        if jsonBlock[resourceAttribute][0][resourceSubAttribute] and jsonBlock[resourceAttribute][0][resourceSubAttribute] != None:
                                                                            resourceList[resourceType][resourceName][resourceAttribute][0][resourceSubAttribute] = jsonBlock[resourceAttribute][0][resourceSubAttribute] 
                                                except Exception as e:
                                                    print("Something went wrong when trying to get existence value")
                                                    traceback.print_exc()
                                            if flagFound == True:
                                                break
                                else:  
                                    tempValue = "ZODIAC-INIT"              
                                    if newValue == "true" or newValue == "True":
                                        tempValue = True
                                    elif newValue == "false" or newValue == "False":
                                        tempValue = False
                                    elif newValue == "":
                                        tempValue = None
                                    elif newValue.isnumeric():
                                        tempValue = int(newValue)
                                    else:
                                        tempValue = newValue
                                    if tempValue == "ZODIAC-INIT":
                                        continue
                                    if type(resourceValue) == list:
                                        resourceValue = [tempValue]
                                    else:
                                        resourceValue = tempValue
                                    if len(targetResourceAttributeList) == 1:
                                        resourceList[resourceType][resourceName][resourceAttribute] = resourceValue
                                    elif len(targetResourceAttributeList) == 2:
                                        if "ThenUnequal" in testRule[1] or "ThenCIDRExclude" in testRule[1]:
                                            for tempIndex in range(len(resourceList[resourceType][resourceName][resourceAttribute])):
                                                resourceList[resourceType][resourceName][resourceAttribute][tempIndex][resourceSubAttribute] = resourceValue
                                        else:
                                            resourceList[resourceType][resourceName][resourceAttribute][attributeIndex][resourceSubAttribute] = resourceValue
            if len(resourceJsonData["resource"]) == 0:
                del(resourceJsonData["resource"])                            
            with open(f"{tfFile}", 'w') as f:
                json.dump(resourceJsonData, f, indent = 4)            
        return True, resourceGroupList, GENResourceSet
    except Exception as e:
        print(f"GEN json configuration construction failed: {e}!")
        traceback.print_exc()
        return False, [], set()
if __name__ == "__main__":
    pass
    