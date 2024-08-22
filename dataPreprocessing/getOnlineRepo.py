### This script crawls Terraform repositories as zip files from
### GitHub using the GitHub REST API (https://developer.github.com/v3/search/).

import os
import sys
sys.path.insert(0, '..')
import json
import wget
import time
import csv
import requests
import math
import utils.utils as utils
import multiprocessing
from dataPreprocessing.getCloudRegistry import check_call
import argparse

URL = "https://api.github.com/search/code?q="  # The basic URL to use the GitHub API
#SUB_QUERIES = ["&created%3A>%3D2018-03-31"]  # Different sub-queries if you need to collect more than 1000 elements
PARAMETERS = "&per_page=100"  # Additional parameters for the query (by default 100 items per page)
DELAY_BETWEEN_QUERIES = 20  # The time to wait between different queries to GitHub (to avoid be banned)
OUTPUT_FOLDER = "./repos/"  # Folder where ZIP files will be stored
OUTPUT_CSV_FILE = "./repositories.csv"  # Path to the CSV file generated as output

def getUrl(url, token):
    """ Given a URL it returns its body """
    headers = {
        'Authorization': 'Token {}'.format(token)
    }
    response = requests.request("GET", url, headers=headers)
    #print(response.text)
    return response.json()

### Get provider resource types through resource schema
def parseProviderResourceType(filename):
    f = open(filename)
    data = json.load(f)
    providerName = filename.split(".")[0]
    resource_schemas = data['provider_schemas'][f'registry.terraform.io/hashicorp/{providerName}']['resource_schemas']
    data_source_schemas = data['provider_schemas'][f'registry.terraform.io/hashicorp/{providerName}']['data_source_schemas'] 
    resourceTypes = set()
    for resourceType in resource_schemas:
        resourceTypes.add(resourceType)
        print(resourceType)
    return resource_schemas

### Get repo by resource type and repo size, this is very error prone for now...
def getRepoByResourceType(zipDirectory, resourceNames, SUB_QUERIES, maxCount, token):
    if not os.path.exists(zipDirectory):
        os.mkdir(zipDirectory)
    resources = "+".join(resourceNames)
    QUERY = f"{resources}+in:file+language:HCL"  # The personalized query
    #QUERY = f"{resources}"
    downloadedFiles = set()

    # Output CSV file which will contain information about repositories
    csv_file = open(OUTPUT_CSV_FILE, 'a')
    repositories = csv.writer(csv_file, delimiter=',')

    # Run queries to get information in json format and download ZIP file for each repository
    countOfRepositories = 0
    for subquery in range(1, len(SUB_QUERIES) + 1):
        print("Processing subquery " + str(subquery) + " of " + str(len(SUB_QUERIES)) + " ...")
        # Obtain the number of pages for the current subquery (by default each page contains 100 items)
        url = URL + QUERY + str(SUB_QUERIES[subquery - 1]) + PARAMETERS
        try:
            data = json.loads(json.dumps(getUrl(url, token)))
            print(url, token, data)
            numberOfPages = int(math.ceil(data['total_count'] / 100.0))
        except:
            continue
        print("No. of pages = " + str(numberOfPages))

        # Results are in different pages
        for currentPage in range(1, numberOfPages + 1):
            print("Processing page " + str(currentPage) + " of " + str(numberOfPages) + " ...")
            url = URL + QUERY + str(SUB_QUERIES[subquery - 1]) + PARAMETERS + "&page=" + str(currentPage)
            #url = URL + QUERY + PARAMETERS + "&page=" + str(currentPage)
            print("Github API call url:", url)
            data = json.loads(json.dumps(getUrl(url, token)))
            # Iteration over all the repositories in the current json content page
            #print(data['items'])
            try:
                for item in data['items']:
                    
                    repository = item['name']
                    # Download the zip file of the current project
                    print("\nDownloading repository '%d','%s' ..." % (countOfRepositories,repository))
                    #print("The repo is created at: ", item['repository']['created_at'])
                    url = item['repository']['html_url']
                    fileToDownload = url[0:len(url)] + "/archive/refs/heads/master.zip"
                    if fileToDownload in downloadedFiles:
                        continue
                    else:
                        downloadedFiles.add(fileToDownload)
                        print(fileToDownload)
                    fileName = item['repository']['full_name'].replace("/", "#") + ".zip"
                    if "ChatNow" in fileName:
                        continue
                    try:
                        wget.download(fileToDownload, out=zipDirectory + fileName)
                        utils.execute_cmd(f"cd {zipDirectory}; find -type f \\( -name \"*zip\" -o -name \"*tar\" -o -name \"*gz\" \\) -size +1M -delete")
                        repositories.writerow([repository, url, "downloaded"])
                    except Exception as e:
                        print("Could not download file {}".format(fileToDownload))
                        print(e)
                        repositories.writerow([repository, url, "error when downloading"])
                    # Update repositories counter
                    countOfRepositories = countOfRepositories + 1
                    if countOfRepositories >= maxCount:
                        break
            except:
                print("cannot read url from the current page!")
            if countOfRepositories >= maxCount:
                break 
        # A delay between different sub-queries
        if subquery < len(SUB_QUERIES):
            print("Sleeping " + str(DELAY_BETWEEN_QUERIES) + " seconds before the new query ...")
            time.sleep(DELAY_BETWEEN_QUERIES)

    print("\nDONE! " + str(countOfRepositories) + " repositories have been processed.")
    csv_file.close()

### Subprocess to unzip a collected zip format github repo.
def call_unzip(zipDirectory, directory, file):
    print("unzip file: ", file)
    try:
        cmd = f"unzip -o {zipDirectory+file} -d {directory}/"
        utils.execute_cmd(cmd)
    except:
        print("Something went wrond during unzip")

### Main function to unzip all collected github repos.
def unzipRepos(zipDirectory, directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    cmd = f"rm -rf {directory}/*"
    utils.execute_cmd(cmd)
    arglists = []
    for file in os.listdir(zipDirectory):
        arglists.append([zipDirectory, directory, file])
    pool = multiprocessing.Pool(processes=8)
    for arglist in arglists:
        pool.apply_async(call_unzip, args=arglist)
    pool.close()
    pool.join()

### Eliminate depends_on attributes in collected terraform configs.
def eliminateDependsOn(directory, outputDirectory):
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)
    utils.execute_cmd_imm(f"cp -r {directory}/* {outputDirectory}/")
    count = 0
    for filename in os.listdir(outputDirectory):
        try:
            fi = os.path.join(outputDirectory, filename)
            count += 1
            print(count, outputDirectory, filename)
            tfDirectories = utils.execute_cmd_imm(f"find {fi} -name \"*.tf\"")
            mainTFFiles = tfDirectories.split("\n")[:-2]
            for mainTFFile in mainTFFiles:
                outputContent = ""
                with open(mainTFFile, "r") as fFile:
                    line = fFile.readline()
                    while line:
                        if "depends_on" not in line:
                            outputContent += line
                        line = fFile.readline()
                with open(mainTFFile, "w") as fFile:
                    fFile.write(outputContent)
        except:
            print("Something went wrong with {filename} during depends_on elimination")

### Get the graph representation for all the collected Terraform configs.
def getGraphRepresentation(directory, outputDirectory):
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)
    count = 0
    index = 0
    arglists = []
    for filename in os.listdir(directory):
        count += 1
        f = os.path.join(directory, filename)
        print(count, directory, filename)
        tfDirectories = utils.execute_cmd_imm(f"find {f} -name \"*.tf\"")
        #time.sleep(1)
        mainTFFiles = tfDirectories.split("\n")[:-2]
        dirSet, minDirDepth = set(), 65536
        for mainTFFile in mainTFFiles[:5]:
            currDirDepth = len(mainTFFile.split("/"))
            if currDirDepth < minDirDepth:
                minDirDepth = currDirDepth
            dirSet.add(("/".join(mainTFFile.split("/")[:-1]), currDirDepth))   
            
        rootDirList = []
        for dir, depth in dirSet:
            if depth == minDirDepth:
                rootDirList.append(dir)
        for rootDir in rootDirList:
            index += 1
            print(rootDir)
            name = "_".join(rootDir.split("/")[2:])
            arglists.append([rootDir, index, outputDirectory, name]) 
            
    pool = multiprocessing.Pool(processes=8)
    for arglist in arglists:
        pool.apply_async(check_call, args=arglist)
    pool.close()
    pool.join()
    print("Get graph representation finished!")

def removeIrrelevantFiles(inputDirectory, outputDirectory):
    count = 0
    utils.execute_cmd_imm(f"cp -r {inputDirectory} {outputDirectory}")
    for filename in os.listdir(outputDirectory):
        count += 1
        f = os.path.join(outputDirectory, filename)
        print(count, outputDirectory, filename)
        utils.execute_cmd_imm(f'find {f} -type f  ! -name "*.tf*"  -delete')
        
def gatherReposByResourceType(resourceType, token):
    sizeList = [f"+size%3A{i*1000+1}..{(i+1)*1000+1}" for i in range(0,20)]
    getRepoByResourceType(f"../repoFiles/repos_{resourceType}/", [resourceType], sizeList, 2000, token)
    unzipRepos(f"../repoFiles/repos_{resourceType}/", f"../folderFiles/folders_{resourceType}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--actions", help="what actions to perform?", nargs='?', default = "crawl")
    parser.add_argument("--resource_name", help="the name of the resource we want to get")
    parser.add_argument("--token", help="your github authorization token", default = "")
    args = parser.parse_args()
    return args

### Usage example 1: sudo python3 -u getOnlineRepo.py --resource_name ALL
### Usage example 2: timeout 6000 sudo python3 -u getOnlineRepo.py --resource_name azurerm_application_gateway
### Usage example 3: timeout 6000 sudo python3 -u getOnlineRepo.py --resource_name azurerm_application_gateway --actions unzip
if __name__ == "__main__":
    args = parse_args()
    if not os.path.exists("../repoFiles"):
        os.mkdir("../repoFiles")
    if not os.path.exists("../folderFiles"):
        os.mkdir("../folderFiles")
    resourceType = str(args.resource_name)
    token = str(args.token)
    if str(args.actions) == "crawl":
        if resourceType != "ALL":
            gatherReposByResourceType(resourceType, token)
        else:
            resourceList = json.load(open("../resourceList.json", "r"))
            for resourceName in resourceList:
                gatherReposByResourceType(resourceName, token)
    elif str(args.actions) == "unzip":
        if resourceType != "ALL":
            unzipRepos(f"../repoFiles/repos_{resourceType}/", f"../folderFiles/folders_{resourceType}")
        else:
            resourceList = json.load(open("../resourceList.json", "r"))
            for resourceName in resourceList:
                unzipRepos(f"../repoFiles/repos_{resourceName}/", f"../folderFiles/folders_{resourceName}")
    else:
        print("Invalid actions!")