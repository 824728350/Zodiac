### This script crawls provider plugin implementation and extract 
### basic Terraform resource usage examples 

import os
import sys
sys.path.insert(0, '..')
import utils.utils as utils
from threading import Timer
from collections import defaultdict
import multiprocessing

### This call was used to get the tflint/graph representation of a directory.
def check_call(mainDir, count, receiverDir, name):
    if not os.path.exists(mainDir):
        os.mkdir(mainDir)
    print("Directory:", mainDir)
    terraform_init_result = utils.execute_cmd_imm(f"cd {mainDir}; /usr/bin/timeout 60 terraform init -upgrade -input=false")
    if terraform_init_result != "Failure":
        print("Terraform init succeeded!")
    else:
        print("Terraform init failed!")
        utils.execute_cmd_imm(f"rm -rf {mainDir}/.terraform")
        return
    
    try:
        utils.execute_cmd_imm(f"cd {mainDir}; terraform graph > graph.out")
        utils.execute_cmd_imm(f"cp {mainDir}/graph.out {receiverDir}/{name}.out")
        utils.execute_cmd_imm(f"cd {mainDir}; tflint --module .")
        utils.execute_cmd_imm(f"cp {mainDir}/tflint.json {receiverDir}/{name}.json")
        utils.execute_cmd_imm(f"rm -rf {mainDir}/.terraform")
        print(f"Terraform graph {name} succeeded, count {count}.")
    except:
        print("get a problem during terraform graph generation!!")
 
### This is a subprocess for getting usage examples from cloud registry html files,
### for the purpose of converting identified lines of code into terraform configs.
def genTFFromDoc(mainDir, codeSnippet, count, receiverDir):
    if not os.path.exists(mainDir):
        os.mkdir(mainDir)
    outputFile = open(mainDir+"/main.tf", "w")
    outputFile.write(codeSnippet)
    outputFile.close()
    if receiverDir:
        name = "graph_" + mainDir.split("/")[-1]
        check_call(mainDir, count, receiverDir, name)

### This is the main function for identifying usage examples from cloud registry html files.
def getFromCloudRegistry(directory, outputDir, receiverDir):
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
    codeSnippetDict = defaultdict(list)
    for filename in os.listdir(directory):
        if ".markdown" in filename:
            print(filename)
            fullName = os.path.join(directory, filename)
            f = open(fullName, "r")
            line = f.readline()
            codeSnippet = ""
            flagSnippet = 0
            while line:
                if "```hcl" in line or "```terraform" in line:
                    flagSnippet = 1
                elif flagSnippet == 1 and "```" in line:
                    flagSnippet = 0 
                    codeSnippetDict[filename.split(".")[0]].append(codeSnippet)
                    codeSnippet = ""
                elif flagSnippet == 1:
                    codeSnippet += line
                line = f.readline()
    count = 0
    arglists = []
    for key in codeSnippetDict:
        count += 1
        index = 0
        for codeSnippet in codeSnippetDict[key]:
            index += 1
            mainDir = outputDir+key+"_"+str(index)
            arglists.append([mainDir, codeSnippet, count, receiverDir]) 
    if receiverDir:
        if not os.path.exists(receiverDir):
            os.mkdir(receiverDir)
    pool = multiprocessing.Pool(processes=8)
    for arglist in arglists:
        #print("Arguments list: ",arglist)
        pool.apply_async(genTFFromDoc, args=arglist)
    pool.close()
    pool.join()

### Specific call to turn Azure registry usage examples into config files.
def getFromAzureRegistry():
    utils.execute_cmd_imm(f"rm -rf terraform-provider-azurerm")
    utils.execute_cmd_imm(f"git clone https://github.com/hashicorp/terraform-provider-azurerm")
    directory, outputDir = "./terraform-provider-azurerm/website/docs/r", "./terraform-provider-azurerm/usageExamples/"
    ### get graph and tflint representation if needed, otherwise skip
    ### receiver = "./terraform-provider-azurerm/outputRegistryGraph"
    receiver = None
    getFromCloudRegistry(directory, outputDir, receiver)

def getFromGoogleRegistry():
    utils.execute_cmd_imm(f"rm -rf terraform-provider-google")
    utils.execute_cmd_imm(f"git clone https://github.com/hashicorp/terraform-provider-google")
    directory, outputDir = "./terraform-provider-google/website/docs/r", "./terraform-provider-google/usageExamples/"
    receiver = None
    getFromCloudRegistry(directory, outputDir, receiver)
    
def getFromAWSRegistry():
    utils.execute_cmd_imm(f"rm -rf terraform-provider-aws")
    utils.execute_cmd_imm(f"git clone https://github.com/hashicorp/terraform-provider-aws")
    directory, outputDir = "./terraform-provider-aws/website/docs/r", "./terraform-provider-aws/usageExamples/"
    receiver = None
    getFromCloudRegistry(directory, outputDir, receiver)          

### Usage example: python3 getCloudRegistry.py > output1
if __name__ == "__main__":
    getFromAzureRegistry()
    
