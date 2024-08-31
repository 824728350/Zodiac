### This scripts translates crawled Terraform programs into Rego compatible format.
### It also performs a sequence of code transformations to make sure these Terraform
### programs are indeed plannable. 
import os
import sys
sys.path.insert(0, '..')
import utils.utils as utils
import multiprocessing
import json
from collections import defaultdict
import string
import random
import glob
import argparse

### Uniformed provider blocks to replace ad-hoc user preferences which may cause issues.
PROVIDER_AZURERM = """
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.116.0"
    }
  }
}

provider "azurerm" {
 storage_use_azuread = true
 features {}
}
"""
PROVIDER_GOOGLE = """
provider "google" {
 project   = "ZODIAC"
 region   = "us-central1"
}
"""

PROVIDER_AWS = """
provider "aws" {
 region           = "us-east-1"
 skip_credentials_validation = true
 skip_requesting_account_id = true
 skip_metadata_api_check   = true
 s3_force_path_style     = true
 access_key         = "mock_access_key"
 secret_key         = "mock_secret_key"
}
"""

PUBLIC_KEY = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTcNZBXea8DCFaCXUuH0xUWBa5zv2YRXBKSnRAaIcwF2fRJxFdG/PgnJ4HoA10id8dSILVSuXLLjp9sTtqNgtnErKy/+zTPXcb6seHd/MycZb5181jYIIyLCuYrf2ZHum4PlMQ3RQUelbjY1ye/k54rmgdx9gmKzvy0v0oyRd1XSat0mvvVm1QesVcu4qV0uyBHga+XYm6mYhJAucNLbwB9JU/gHCc4yidckWzFsFyrosZtmbEi5C8hXNojJIeMBMFoaQSO4eZHtNhlXpscRt8+WzPqS1V/6t3wa/XjdFjZPHFQOjTPBb5dZaF5Fh2lxRDM8oYPxmuVrLPlscdqGJr noname"""
PRIVATE_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcnNhAAAAAwEAAQAAAQEA03DWQV3mvAwhWgl1Lh9MVFgWuc79mEVwSkp0QGiHMBdn0ScRXRvz4JyeB6ANdInfHUiC1Urlyy46fbE7ajYLZxKysv/s0z13G+rHh3fzMnGW+dfNY2CCMiwrmK39mR7puD5TEN0UFHpW42Ncnv5OeK5oHcfYJis78tL9KMkXdV0mrdJr71ZtUHrFXLuKldLsgR4Gvl2JupmISQLnDS28AfSVP4BwnOMonXJFsxbBcq6LGbZmxIuQvIVzaIySHjATBaGkEjuHmR7TYZV6bHEbfPlsz6ktVf+rd8Gv143RY2TxxUDo0zwW+XWWheRYdpcUQzPKGD8Zrlayz5bHHahiawAAA8AE4vH1BOLx9QAAAAdzc2gtcnNhAAABAQDTcNZBXea8DCFaCXUuH0xUWBa5zv2YRXBKSnRAaIcwF2fRJxFdG/PgnJ4HoA10id8dSILVSuXLLjp9sTtqNgtnErKy/+zPXcb6seHd/MycZb5181jYIIyLCuYrf2ZHum4PlMQ3RQUelbjY1ye/k54rmgdx9gmKzvy0v0oyRd1XSat0mvvVm1QesVcu4qV0uyBHga+XYm6mYhJAucNLbwB9JU/gHCc4yidckWzFsFyrosZtmbEi5C8hXNojJIeMBMFoaQSO4eZHtNhlXpscRt8+WzPqS1V/6t3wa/XjdFjZPHFQOjTPBb5dZaF5Fh2lxRDM8oYPxmuVrLPlscdqGJrAAAAAwEAAQAAAQBg6GV6niQDaffbQVxwoC2mtpzr2l/Ga4T0t70iTAYx13hgluxRZV9YQc/4JLYmBI666CH2yhYaEn0CYLmfi1ecjShT/BI6GwC9TdTXVPWk2ATfS7Y55uClSDNPDeeeR1nNdNszbnAmlo++NiscP+gNTbowdAiwLb6TI3qeN9RFmG9xrTw72za5JfwapFLHHmrLWGk2VGew0S/oJyQlS7yqgfZO/vbtjFbryFJ71lYZw5F9fJG90lOeLJQlpU1e++0KZgexysgpPb+TlWRhIy4hHTswiox/ST+svFLduY0m8wSHb9vFDIXIwCg7yu9ijIGDD/dJ8w86ToxaZqvdEYqZAAAAgQDMqQ2A0sQJlDkn0DNo1onrb4RXzXgVygT6GwGHmW5Uq86FBR8j2VJmAx61pKEJWGWP/7kW84F6+hMlSVlK4oPtPhhSkIqRxtlDToppWU8xCSHmfw9SZl4DDlYaY7gwVeUWKVQCC+QPl+0/YRgXLMM3iARTe4l+DEckerzUBFEYZwAAAIEA9VvDlA9Er8wkAfQGY2xqN5xtKeCvahlxpJBEaXcIeqq4doOmXGprDaiqJWGkxNp2JAA66HQBeZAuft+AI/yRZrbsnOP6k/9GrJ/TC2gAqSrptSwRAAnXr8AjhiPjEICVU8VxWa2+4XfZAr2gkAGQdD/54CA70HpFQijLdAqPbW8AAACBANyce2QD52k5IKQotMQQKan+ofFs2YwSbwX7AjXazm7+1K4dE/DkKMD6zih7TWhDN23Qp4U2+pi3QGAiUbQcGl+DmWNDRFXk+3i1ob2M9iip7+hXI3CEtQ/W+1inVLd0mde2QWntld3wxEszzecB3/2WnadN038598OAmEDly5TFAAAABm5vbmFtZQECAwQ=-----END OPENSSH PRIVATE KEY-----"""

### Clean up collected repos! This is very important, because provider attributes and file names
### are major sources of terraform plan and deploy bugs. One current missing piece is whether we should
### do advanced "cleans" such as manually filling in variable values if they are unknown, but the 
### concern is whether they could cause other problems such as fake depdencies.
def cleanUpDir(directory, provider):
    tfDirectories = utils.execute_cmd_imm(f"find {directory} -name \"*.tf\"")
    #time.sleep(1)
    mainTFFiles = tfDirectories.split("\n")[:-1]
    providerFlag = False
    providerAzureFlag, providerGoogleFlag, providerAWSFlag = False, False, False
    for mainTFFile in mainTFFiles:
        try:
            ### rewrite tf files so that we do not to have to worry about providers and files.
            fileContent = ""
            f_tf_r = open(mainTFFile, "r")
            line = f_tf_r.readline()
            while line:
                if "public" in line and "key" in line and "file(" in line:
                    fileContent += line[:line.find("=")+1]
                    countBracket = line.count("(") - line.count(")")
                    while countBracket != 0 and countLine < 100: 
                        line = f_tf_r.readline()
                        countBracket += line.count("(") - line.count(")")
                        countLine += 1
                    fileContent += '"' + PUBLIC_KEY + '"' + "\n"
                    print("Public key overwrite", line)
                elif "private" in line and "key" in line and "file(" in line:
                    fileContent += line[:line.find("=")+1]
                    countBracket = line.count("(") - line.count(")")
                    while countBracket != 0 and countLine < 100: 
                        line = f_tf_r.readline()
                        countBracket += line.count("(") - line.count(")")
                        countLine += 1
                    fileContent += '"' + PRIVATE_KEY + '"' + "\n"
                    print("Private key overwrite", line)
                elif "file(" in line:
                    fileContent += line[:line.find("=")+1]
                    countBracket = line.count("(") - line.count(")")
                    while countBracket != 0 and countLine < 100: 
                        line = f_tf_r.readline()
                        countBracket += line.count("(") - line.count(")")
                        countLine += 1
                    fileContent += '"' + "FILENAME PLACEHOLDER" + '"' +"\n"
                    print("File path overwrite", line)
                elif "provider " in line and "\"azurerm\"" in line and "{" in line and providerAzureFlag == False:
                    providerFlag = True
                    providerAzureFlag = True
                    print("Provider AzureRM overwrite", line)
                    countLine = 0
                    countBracket = line.count("{") - line.count("}")
                    while countBracket != 0 and countLine < 100: 
                        line = f_tf_r.readline()
                        countBracket += line.count("{") - line.count("}")
                        countLine += 1
                    fileContent += PROVIDER_AZURERM
                elif "provider " in line and "\"google\"" in line and "{" in line and providerGoogleFlag == False:
                    providerFlag = True
                    providerGoogleFlag = True
                    print("Provider Google overwrite", line)
                    countLine = 0
                    countBracket = line.count("{") - line.count("}")
                    while countBracket != 0 and countLine < 100: 
                        line = f_tf_r.readline()
                        countBracket += line.count("{") - line.count("}")
                        countLine += 1
                    fileContent += PROVIDER_GOOGLE
                elif "provider " in line and "\"aws\"" in line and "{" in line and providerAWSFlag == False:
                    providerFlag = True
                    providerAWSFlag = True
                    print("Provider AWS overwrite", line)
                    countLine = 0
                    countBracket = line.count("{") - line.count("}")
                    while countBracket != 0 and countLine < 100: 
                        line = f_tf_r.readline()
                        countBracket += line.count("{") - line.count("}")
                        countLine += 1
                    fileContent += PROVIDER_AWS
                elif "terraform " in line[:len("terraform ")] and "{" in line:
                    print("Terraform backend overwrite", line)
                    countLine = 0
                    countBracket = line.count("{") - line.count("}")
                    while countBracket != 0 and countLine < 100:
                        line = f_tf_r.readline()
                        countBracket += line.count("{") - line.count("}")
                        countLine += 1
                    fileContent += ""
                else:
                    fileContent += line
                
                line = f_tf_r.readline()
            f_tf_r.close()
            f_tf_w = open(mainTFFile, "w")
            if "backend.tf* " in mainTFFile:
                f_tf_w.write("")
            else:
                f_tf_w.write(fileContent)
            f_tf_w.close()
        except:
            print(f"Something went wrong when cleaning {mainTFFile}")
            
    if providerFlag == False:
        for mainTFFile in mainTFFiles:
            try:
                if "main" in mainTFFile or "provider" in mainTFFile:
                    f_tf_r = open(mainTFFile, "r")
                    if provider == "azurerm":
                        fileContent = PROVIDER_AZURERM
                    elif provider == "google":
                        fileContent = PROVIDER_GOOGLE
                    elif provider == "aws":
                        fileContent = PROVIDER_AWS
                    else:
                        fileContent = PROVIDER_AZURERM + PROVIDER_GOOGLE + PROVIDER_AWS
                    line = f_tf_r.readline()
                    while line:
                        fileContent += line
                        line = f_tf_r.readline()
                    f_tf_r.close()
                    f_tf_w = open(mainTFFile, "w")
                    f_tf_w.write(fileContent)
                    f_tf_w.close()
                    break
            except:
                print(f"Something went wrong when injecting provider into {mainTFFile}")
            
### Subprocess to call regula to generate json file for individual .tf file.
def call_regula(count, outputDirectory, filepath):
    print(count, filepath)
    utils.execute_cmd_imm(f"rm -rf *.rego")
    utils.execute_cmd_imm(f"cd {filepath}; /usr/bin/timeout 60 regula write-test-inputs .")
    regoDirectories = utils.execute_cmd_imm(f"find {filepath} -name \"*_tf.rego\"")
    mainTFFiles = regoDirectories.split("\n")[:-1]
    for mainTFFile in mainTFFiles[:1000]:
        try:
            renamedFile = "#".join(mainTFFile.split("/")[1:])
            utils.execute_cmd_imm(f"cp {mainTFFile} {outputDirectory}/{renamedFile}")
        except:
            print("Something went wrong when calling regula parser")

### Main function to to call regula to generate config rego files for all collected repos.
def getRegoConfigFormat(directory, outputDirectory, incremental):
    if incremental == False:
        utils.execute_cmd_imm(f"rm -rf {outputDirectory}")
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)
    count = 0
    arglists = []
    for filename in os.listdir(directory):
        count += 1
        filepath = os.path.join(directory, filename)
        arglists.append([count, outputDirectory, filepath])
        
    pool = multiprocessing.Pool(processes=8)
    for arglist in arglists:
        pool.apply_async(call_regula, args=arglist)
    pool.close()
    pool.join()
    print("Get rego format finished!")

### Subprocess to call hcl2json to generate json file for individual .tf file.
def call_hcl2json(count, outputDirectory, filepath):
    print(count, filepath)
    try:
        search_criteria = os.path.join(filepath, '**/*.tf')
        for TFfileName in glob.iglob(search_criteria, recursive=True):
            TFfileID = TFfileName[:-3]
            jsonFileName = f"{TFfileID}.json"
            utils.execute_cmd_imm(f"cd {filepath}; /usr/bin/timeout 20 hcl2json {TFfileName} > {jsonFileName} 2>temp")
            try:
                count_layer = len(filepath.split("/")) - 1
                renamedFile = "#".join(jsonFileName.split("/")[count_layer:])
                utils.execute_cmd_imm(f"/usr/bin/timeout 10 cp {jsonFileName} {outputDirectory}/{renamedFile} 2>temp")
            except:
                print("Something went wrong when calling hcl2json parser", jsonFileName, "jsonFileName")
    except:
        print("Something went wrong when calling hcl2json parser", filepath, "filepath")
        
### Main function to to call hcl2json to generate config json files for all collected repos.
def getJsonFormat(directory, outputDirectory, incremental):
    if incremental == False:
        print(f"rm -rf {outputDirectory}")
        utils.execute_cmd_imm(f"rm -rf {outputDirectory}")
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)
    count = 0
    arglists = []
    for filename in os.listdir(directory):
        count += 1
        filepath = os.path.join(directory, filename)
        arglists.append([count, outputDirectory, filepath])
        
    pool = multiprocessing.Pool(processes=16)
    for arglist in arglists:
        pool.apply_async(call_hcl2json, args=arglist)
    pool.close()
    pool.join()
    print("Get rego json format finished!")

### Main function to to call hcl2json to generate config rego files for all collected repos.
def getRegoJsonFormat(directory, outputDirectory, incremental):
    if incremental == False:
        print(f"rm -rf {outputDirectory}")
        utils.execute_cmd_imm(f"rm -rf {outputDirectory}")
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        fi = open(filepath, "r")
        result = "mock_config := " + fi.read()
        fi.close()
        outputFilepath = os.path.join(outputDirectory, ".".join(filename.split(".")[:-1])+".rego")
        fo = open(outputFilepath, "w")
        fo.write(result)
        fo.close()     
        
### Subprocess to call regula to generate rego file for terraform plan
### All the preprocessing goes here, including terraform init and plan, as well as
### terraform to json format transformation, and rego format generation using regula.
def call_terraform_regula(mainDir, count, receiverDir, name, filteredDirectory):
    try:
        if not os.path.exists(mainDir):
            os.mkdir(mainDir)
        print("Main Directory:", mainDir, count)
        utils.execute_cmd_imm(f"rm -rf {mainDir}/.terraform*")
        utils.execute_cmd_imm(f"rm -rf {mainDir}/*.tfstate*")
        utils.execute_cmd_imm(f"rm -rf {mainDir}/*.rego")
        utils.execute_cmd_imm(f"rm -rf {mainDir}/*.tf.json")
        utils.execute_cmd_imm(f"rm -rf {mainDir}/plan_handling.json")
        utils.execute_cmd_imm(f"rm -rf {mainDir}/plan_temp.json")
        terraform_init_result = utils.execute_cmd_imm(f"cd {mainDir}; /usr/bin/timeout 90 time terraform init -input=false")
        if terraform_init_result != "Failure":
            print("Terraform init succeeded! ", count)
        else:
            print("Terraform init failed! ", count)
            utils.execute_cmd_imm(f"rm -rf {mainDir}/.terraform*")
            return
        terraform_plan_result = utils.execute_cmd_imm(f"cd {mainDir}; sudo /usr/bin/timeout 90 time terraform plan -refresh=false -out=plan.tfplan -input=false")
        if terraform_plan_result != "Failure":
            print("Terraform plan succeeded! ", count)
        else:
            print("Terraform plan failed! ", count)
            utils.execute_cmd_imm(f"rm -rf {mainDir}/.terraform*")
            return
        
        utils.execute_cmd_imm(f"cd {mainDir}; /usr/bin/timeout 60 time terraform show -json plan.tfplan >plan.json")
        utils.execute_cmd_imm(f"cd {mainDir}; /usr/bin/timeout 60 time regula write-test-inputs plan.json")
        utils.execute_cmd_imm(f"cp {mainDir}/plan_json.rego {receiverDir}/{name}.rego")
        utils.execute_cmd_imm(f"rm -rf {mainDir}/.terraform*")
        print(f"Terraform regula {name} succeeded, count {count}.")
        if not os.path.exists(f"{filteredDirectory}/{name}"):
            utils.execute_cmd_imm(f"cp -r {mainDir} {filteredDirectory}/{name}")
        
    except:
        print("get a problem during terraform regula generation!!")

### Sometimes variable values are in *.tfvars.example files, we need to move them to *.tfvars
def formatTFVars(directory):
    tfVarsString = utils.execute_cmd_imm(f"find {directory} -name \"*.tfvars.*\"")
    tfVarsFiles = tfVarsString.split("\n")[:-1]
    for tfVarsFile in tfVarsFiles:
        if ".example" in tfVarsFile:
            result = ""
            try:
                fi = open(tfVarsFile, "r")
                line = fi.readline()
                while line:
                    result += line
                    line = fi.readline()
                fi.close()
            except:
                print("Something went wrong when trying to read tfvars examples")
            utils.execute_cmd_imm(f"rm -rf {tfVarsFile}")
            tfVarsFileUsable = tfVarsFile[:tfVarsFile.find(".example")]
            fo = open(f"{tfVarsFileUsable}", "w")
            fo.write(result)
            fo.close()

### FIX ME: this is supposed to fill in default variable values in case there is no usable values in the repo
def fillVariables(directory):
    tfFileString = utils.execute_cmd_imm(f"find {directory} -name \"*.tf\"")
    tfFiles = tfFileString.split("\n")[:-1]
    for tfFile in tfFiles:
        print("fillVariables", tfFile)
        try:
            fi = open(tfFile, "r")
            line = fi.readline()
            resultString = ""
            while line:
                if line[:len("variable")] == "variable" and "{" in line:
                    tempString = line
                    bracketDomain = line.count("{") - line.count("}")
                    defaultFlag = False
                    typeFlag = "null"
                    repString = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + "hold"
                    
                    if "location" in line or "region" in line:
                        typeFlag = "string"
                        repString = "eastus"
                    elif "address_space" in line or "cidr" in line or "address_prefix" in line or "ip" in line:
                        typeFlag = "string"
                        repString = "10.0.0.0/16"
                    elif "prefix" in line:
                        typeFlag = "string"
                        repString = "zodiac"
                    elif "sku" in line:
                        repString = "Standard"
                        
                    countLines = 0
                    while (bracketDomain > 0 and countLines <= 50) or (bracketDomain == 0 and countLines == 0):
                        if ("default " in line or "default=" in line) and "description" not in line:
                            defaultFlag = True
                        if "type" in line and " map" in line:
                            typeFlag = "map"
                        elif "type" in line and " list" in line:
                            typeFlag = "list"
                        elif "type" in line and " string" in line:
                            typeFlag = "string"
                        elif "type" in line and " bool" in line:
                            typeFlag = "bool"
                        if (bracketDomain > 0 and countLines <= 50):
                            countLines += 1
                            line = fi.readline()
                            tempString += line
                            bracketDomain += line.count("{") - line.count("}")
                        else:
                            break
                    if countLines >= 50:
                        break
                    
                    if defaultFlag == False:
                        if typeFlag == "list":
                            res = "[]"
                        elif typeFlag == "map":
                            res = "{}"
                        elif typeFlag == "bool":
                            res = "false"
                        elif typeFlag == "string":
                            res = f"\"{repString}\""
                        else:
                            #res = f"\"{repString}\""
                            res = "null"
                        if countLines > 0:
                            tempList = tempString.split("\n")
                            tempList = tempList[:-2] + [f"    default = {res}\n"] + tempList[-2:]
                            resultString += "\n".join(tempList)
                        else:
                            leftBracket = utils.find_nth(tempString, "{", 1)
                            rightBracket = utils.find_nth(tempString, "}", -1)
                            resultString += tempString[:leftBracket+1] + "\n"
                            resultString += "    " + tempString[leftBracket+1:rightBracket] + "\n"
                            resultString += f"    default = \"{res}\"\n"
                            resultString += tempString[rightBracket:] + "\n"
                    else:
                        resultString += tempString
                else:
                    resultString += line
                line = fi.readline()
            fi.close()
            fo = open(tfFile, "w")
            fo.write(resultString)
            fo.close()
        except:
            print(f"Something went wrong when filling variables in {tfFile}")
    
### Main process to call regula to generate rego file for all correctly established terraform plans.
def getRegoPlanFormat(resourceType, directory, outputDirectory, incremental):
    mapNameDirDict = defaultdict()
    if incremental == False:
        utils.execute_cmd_imm(f"rm -rf {outputDirectory}")
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)
    filteredDirectory = directory + "_filtered"
    if not os.path.exists(filteredDirectory):
        os.mkdir(filteredDirectory)
    countTotal, countSum, countImpossible, countPossible = 0, 0, 0, 0
    index = 0
    arglists = []
    for filename in os.listdir(directory):
        countTotal += 1
        f = os.path.join(directory, filename)
        print(countTotal, directory, filename)
        tfDirectories = utils.execute_cmd_imm(f"find {f} -name \"*.tf\"")
        mainTFFiles = tfDirectories.split("\n")[:-1]
        dirSet, minDirDepth = set(), 65536
        for mainTFFile in mainTFFiles[:]:
            currDirDepth = len(mainTFFile.split("/"))
            if currDirDepth < minDirDepth:
                minDirDepth = currDirDepth
            dirSet.add(("/".join(mainTFFile.split("/")[:-1]), currDirDepth))   
            
        rootDirList = []
        for dir, depth in dirSet:
            if depth == minDirDepth:
                rootDirList.append(dir)
        for rootDir in rootDirList[:30]:
            flagVariable = utils.execute_cmd_imm(f"find {rootDir} -name \"variables.tf\"")
            flagTFVar = utils.execute_cmd_imm(f"find {rootDir} -name \"*.tfvars*\"")
            relevant = utils.execute_cmd_imm(f"grep -Rnw '{rootDir}' --include '*.tf' -e '{resourceType}'")
            dataInvolved = utils.execute_cmd_imm(f"grep -Rnw '{rootDir}' --include '*.tf' -e 'data' | grep 'azurerm'")
            if (not relevant or relevant == "Failure") and "terraform-provider" not in resourceType:
                print("Irrelevant dir, please move on!")
                continue
            # if not(not dataInvolved or dataInvolved == "Failure"):
            #     print("Data source involved, please move on!")
            #     continue
            countSum += 1
            
            try:
                utils.execute_cmd_imm(f"cd {directory}; /usr/bin/timeout 10 terraform fmt")
            except:
                countImpossible += 1
                print("A case where it is impossible for the repo to be formatted")
                continue
            if not flagTFVar:
                fillVariables(rootDir)
            else:
                formatTFVars(rootDir)
            if "terraform-provider" in resourceType:
                provider = resourceType.split("-")[-1]
            else:
                provider = "PLACEHOLDER"
            cleanUpDir(rootDir, provider)
            try:
                utils.execute_cmd_imm(f"cd {directory}; /usr/bin/timeout 10 terraform fmt")
            except:
                countImpossible += 1
                print("A case where it is impossible for the repo to be formatted")
                continue
            countPossible += 1
            index += 1
            name = "_".join(rootDir.split("/")[2:])
            print(rootDir, name, flagVariable, flagTFVar)
            mapNameDirDict[name] = rootDir
            arglists.append([rootDir, index, outputDirectory, name, filteredDirectory]) 
            
    with open('mapNameDirDict.json', 'w') as f:
        json.dump(mapNameDirDict, f, sort_keys = True, indent = 4)
    with open(f"../regoFiles/{resourceType}/mapNameDirDict.json", 'w') as f:
        json.dump(mapNameDirDict, f, sort_keys = True, indent = 4)
    print("countTotal: ", countTotal, "countImpossible: ", countImpossible, "countPossible: ", countPossible)
    pool = multiprocessing.Pool(processes=8)
    for arglist in arglists:
        pool.apply_async(call_terraform_regula, args=arglist)
    pool.close()
    pool.join()
    return mapNameDirDict

def getRegoPlanMapping(resourceType, directory):
    mapNameDirDict = defaultdict()
    countTotal = 0
    for filename in os.listdir(directory):
        countTotal += 1
        f = os.path.join(directory, filename)
        print(countTotal, directory, filename)
        tfDirectories = utils.execute_cmd_imm(f"find {f} -name \"*.tf\"")
        mainTFFiles = tfDirectories.split("\n")[:-1]
        dirSet, minDirDepth = set(), 65536
        for mainTFFile in mainTFFiles[:]:
            currDirDepth = len(mainTFFile.split("/"))
            if currDirDepth < minDirDepth:
                minDirDepth = currDirDepth
            dirSet.add(("/".join(mainTFFile.split("/")[:-1]), currDirDepth))   
            
        rootDirList = []
        for dir, depth in dirSet:
            if depth == minDirDepth:
                rootDirList.append(dir)
        for rootDir in rootDirList[:50]:
            name = "_".join(rootDir.split("/")[2:])
            mapNameDirDict[name] = rootDir
    
    print("countTotal: ", countTotal)
    with open('mapNameDirDict.json', 'w') as f:
        json.dump(mapNameDirDict, f, sort_keys = True, indent = 4)
    with open(f"../regoFiles/{resourceType}/mapNameDirDict.json", 'w') as f:
        json.dump(mapNameDirDict, f, sort_keys = True, indent = 4)
    return mapNameDirDict

### Instrument rule template into config rego files, aggregate files in the same directory
### (not recursive) so that we can reduce cross-file dependencies that might be missed.
def instrumentRegoPolicies(directory, outputDirectory, regoCommandString, headerString, upperLimit):
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)
    utils.execute_cmd_imm(f"rm -rf {outputDirectory}/*")
    returnString = ""
    returnString += headerString
    returnString += regoCommandString
    
    fileAggregateDict = defaultdict(list)
    fileDeduplicateCountDict = defaultdict(set)
    fileDeduplicateMapDict = defaultdict(str)
    for filename in sorted(list(os.listdir(directory))):
        if filename.count("#") >= 1:
            filepathID = "#".join(filename.split("#")[:-1])
            fileAggregateDict[filepathID].append(filename)
        if filename.count("#") >= 2:
            filedirID = "#".join(filename.split("#")[:2])
            fileDeduplicateCountDict[filedirID].add(filepathID)
            fileDeduplicateMapDict[filepathID] = filedirID
    
    countPathID = 0
    for filepathID in fileAggregateDict:
        filedirID = fileDeduplicateMapDict[filepathID]
        if filedirID and len(fileDeduplicateCountDict[filedirID]) > 10:
            continue
        print(countPathID, filepathID)
        countPathID += 1
        # Temporary validation data points.
        if countPathID > upperLimit:
            break
        countFile = 0
        pathIDString = returnString
        if len(fileAggregateDict[filepathID]) < 1:
            continue
        for filename in fileAggregateDict[filepathID]:
            filepath = os.path.join(directory, filename)
            lineCount = sum(1 for _ in open(filepath, "r"))
            if lineCount > 5000:
                continue
            countFile += 1
            fileString = ""
            with open(filepath, "r") as f:
                line = f.readline()
                while line:
                    if "mock_config := {" in line:
                        tempString = line
                        tempString = tempString.replace("mock_config", f"mock_config{countFile}")
                        fileString += tempString
                        line = f.readline()
                        while line:
                            fileString += line
                            line = f.readline()
                        break
                    else:
                        line = f.readline()
            pathIDString += fileString + "\n"

        configList = ["mock_config"+str(i) for i in range(1, countFile+1)]
        configListString = ", ".join(configList)
        pathIDString += f"configList := [{configListString}]\n"
        try:  
            with open(outputDirectory+f"/assemble_{filepathID}.rego", "w") as f:
                f.write(pathIDString)
        except:
            print("Something went wrong when trying to instrument rego policies")

### Instrument rules into tfplan rego files, act as an initial step of MDC analysis
def instrumentRegoMinimalDep(directory, outputDirectory, regoCommandString, headerString, upperLimit):
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)
    if directory != outputDirectory:
        utils.execute_cmd_imm(f"rm -rf {outputDirectory}/*")
    returnString = ""
    returnString += headerString
    returnString += regoCommandString
    
    count = 0
    for filename in os.listdir(directory):
        if ".rego" not in filename:
            continue
        filepath = os.path.join(directory, filename)
        lineCount = sum(1 for _ in open(filepath))
        if lineCount < 100 or lineCount > 50000:
            continue
        count += 1
        if count > upperLimit:
            break
        with open(filepath, "r") as f:
            fileString = returnString
            line = f.readline()
            while line:
                if "package" == line[:7] or "import" == line[:6] or "#" == line[0]:
                    line = f.readline()
                    continue
                else:
                    fileString += line
                    line = f.readline()
        outputFilepath = os.path.join(outputDirectory, filename)
        with open(outputFilepath, "w") as f:
            f.write(fileString)  

def getRegoByResource(resourceType):
    if not os.path.exists(f"../regoFiles/{resourceType}"):
        os.mkdir(f"../regoFiles/{resourceType}")
    getRegoPlanFormat(resourceType, f"../folderFiles/folders_{resourceType}", f"../regoFiles/{resourceType}/outputRegoPlanFormat", True)

def getRegoByRegistry(registryType):
    if not os.path.exists(f"../regoFiles/{registryType}"):
        os.mkdir(f"../regoFiles/{registryType}")
    utils.execute_cmd_imm(f"rm -rf ../regoFiles/{registryType}/*")
    ### both folders examples and usageExamples need to be processed!
    getRegoPlanFormat(registryType, f"{registryType}/examples", f"../regoFiles/{registryType}/outputRegoPlanFormat", True)
    getRegoPlanFormat(registryType, f"{registryType}/usageExamples", f"../regoFiles/{registryType}/outputRegoPlanFormat", True)
        
def getJsonByResource(resourceType):
    getJsonFormat(f"../folderFiles/folders_{resourceType}", f"../regoFiles/{resourceType}/outputJsonFormat", False)
    getRegoJsonFormat(f"../regoFiles/{resourceType}/outputJsonFormat", f"../regoFiles/{resourceType}/outputRegoJsonFormat", False)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource_name", help="the name of the resource we want to get", default = "ALL")
    parser.add_argument("--mapping", help="just get the mapping between key and file name, skip other steps", nargs='?', default = "false")
    args = parser.parse_args()
    return args

### Usage example 1: python3 -u getRegoFormat.py --resource_name ALL > output3 2>&1
### Usage example 2: timeout 6000 python3 -u getRegoFormat.py --resource_name azurerm_application_gateway > output4 2>&1
### Usage example 3: timeout 6000 python3 -u getRegoFormat.py --resource_name terraform-provider-azurerm > output5 2>&1
if __name__ == "__main__":
    args = parse_args()
    if not os.path.exists("../regoFiles"):
        os.mkdir("../regoFiles")
    if "true" in args.mapping:
        resource_type = str(args.resource_name)
        getRegoPlanMapping(resource_type, f"../folderFiles/folders_{resource_type}")
    elif "terraform-provider" not in args.resource_name:
        if str(args.resource_name) != "ALL":
            getRegoByResource(str(args.resource_name))
        else:
            resourceList = json.load(open("../resourceList.json", "r"))
            for resourceName in resourceList:
                getRegoByResource(resourceName)
    else:
        getRegoByRegistry(str(args.resource_name))