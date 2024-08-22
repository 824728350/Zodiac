### Main entry for obtaining resource deployment partial order. This
### order is used to guide the later on mining and validation processes. 
import os
import sys
sys.path.insert(0, '..')
import json
from collections import defaultdict
import argparse
import regoMVPGetKnowledgeBase

### Aggregate the depdencies collected from all online repos/usage examples, and
### turn them into a two layer dict, where key1 is parent node while key2 is child node.
def aggregateRegoPartialOrder(jsonDirectory, OrderDict, fileName):
    orderCounter = defaultdict(int)
    for jsonFolderName in os.listdir(jsonDirectory):
        try:
            jsonFolderPath = os.path.join(jsonDirectory, jsonFolderName)
            #for fileName in ["dependencyList.json", "artificialDependencyList.json"]:
            jsonFilePath = os.path.join(jsonFolderPath, fileName)
            jsonData = json.load(open(jsonFilePath, "r"))
            tempCounter = jsonData["result"][0]["expressions"][0]["value"]
            
            for item in tempCounter:
                name1, name2 = item[0], item[1]
                orderCounter[(name1, name2)] += 1
        except:
            print("Something went wrong when executing searching dependency json file!", jsonFilePath)
    
    for key in orderCounter:
        if orderCounter[key] >= 1:
            l, r = key[0].split(".")[0], key[1].split(".")[0]
            if l not in OrderDict:
                OrderDict[l] = defaultdict(int)
            OrderDict[l][r] = orderCounter[key]
    return OrderDict

### Determine whether one node could reach another. Used to detect loops.
def reachable(orderDict, l, r):
    if l == r:
        return True
    if l in orderDict:
        for node in orderDict[l]:
            if reachable(orderDict, node, r):
                return True
    return False

### Since the reachable function is used during merge partial order, this detectLoops 
### function should always return empty.
def detectLoops(graph):
    loops = []
    visited = set()
    def dfs(node, path):
        visited.add(node)
        path.append(node)
        if node not in graph:
            return
        for neighbor in graph[node]:
            if neighbor in path:
                index = path.index(neighbor)
                loop = path[index:]
                loop.sort()
                loop = tuple(loop)
                if loop not in loops:
                    loops.append(loop)
                    print("loops detcted!", loop)
            elif neighbor not in visited:
                dfs(neighbor, path.copy())
    for node in graph:
        if node not in visited:
            dfs(node, [])
    return loops

### Very simple topological sort to get the resource partial order as a list.
def topologicalSort(graph):
    order = []
    visited = set()
    def dfs(node):
        visited.add(node)
        if node not in graph:
            return
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)
        order.insert(0, node)
    for node in graph:
        if node not in visited:
            dfs(node)
    print("Partial order is: ", order)
    with open('../regoFiles/orderList.json', 'w') as f:
        json.dump(order, f, sort_keys = True, indent = 4)
    return order

def cleanOrderDict(repoOrder, repoOrderArtificial, provider):
    orderDict = defaultdict(set)
    implicitOrderDict = defaultdict(set)
    with open('../regoFiles/repoOrderDict.json', 'w') as f:
        json.dump(repoOrder, f, sort_keys = True, indent = 4)
    with open('../regoFiles/repoOrderArtificialDict.json', 'w') as f:
        json.dump(repoOrderArtificial, f, sort_keys = True, indent = 4)
        
    resourceList = regoMVPGetKnowledgeBase.resourceList
    for key in repoOrder:
        for node in repoOrder[key]:
            if not (provider in node and provider in key) or (not node in resourceList) or (not key in resourceList):
                continue
            if (not reachable(orderDict, node, key)):
                orderDict[key].add(node)
                implicitOrderDict[key].add(node)
            else:
                print("Repo implicit partial order self loop detected", key, node)
    for key in repoOrderArtificial:
        for node in repoOrderArtificial[key]:
            if not (provider in node and provider in key) or (not node in resourceList) or (not key in resourceList):
                continue
            if (not reachable(orderDict, node, key)):
                orderDict[key].add(node)
            else:
                print("Repo explicit partial order self loop detected", key, node)
                
    globalSuccessorDict = defaultdict(list)
    globalPredecessorDict = defaultdict(list)
    globalAncestorDict = defaultdict(list)
    globalOffspringDict = defaultdict(list)
    
    for key in implicitOrderDict:
        for node in implicitOrderDict[key]:
            globalSuccessorDict[node].append(key)
            globalPredecessorDict[key].append(node) 
            
    for resourceType1 in resourceList:
        for resourceType2 in resourceList:
            if resourceType1 == resourceType2:
                continue
            if reachable(implicitOrderDict, resourceType1, resourceType2):
                globalAncestorDict[resourceType1].append(resourceType2)
                globalOffspringDict[resourceType2].append(resourceType1)
                
    for resourceType in resourceList:
        if resourceType not in globalPredecessorDict:
            globalPredecessorDict[resourceType] = []
        if resourceType not in globalSuccessorDict:
            globalSuccessorDict[resourceType] = []
        if resourceType not in globalAncestorDict:
            globalAncestorDict[resourceType] = []
        if resourceType not in globalOffspringDict:
            globalOffspringDict[resourceType] = []
        
    with open('../regoFiles/globalSuccessorDict.json', 'w') as f:
        json.dump(globalSuccessorDict, f, sort_keys = True, indent = 4)
    with open('../regoFiles/globalPredecessorDict.json', 'w') as f:
        json.dump(globalPredecessorDict, f, sort_keys = True, indent = 4)
    with open('../regoFiles/globalAncestorDict.json', 'w') as f:
        json.dump(globalAncestorDict, f, sort_keys = True, indent = 4)
    with open('../regoFiles/globalOffspringDict.json', 'w') as f:
        json.dump(globalOffspringDict, f, sort_keys = True, indent = 4)
    return globalSuccessorDict, globalPredecessorDict, globalAncestorDict, globalOffspringDict

    
def getPartialOrderAll(provider):
    repoOrder = defaultdict()
    repoOrderArtificial = defaultdict()
    for resourceType in regoMVPGetKnowledgeBase.resourceList:
        if not os.path.exists(f"../folderFiles/folders_{resourceType}_knowledge"):
            continue
        repoOrder = aggregateRegoPartialOrder(f"../folderFiles/folders_{resourceType}_knowledge", repoOrder, "dependencyList.json")  
        repoOrderArtificial = aggregateRegoPartialOrder(f"../folderFiles/folders_{resourceType}_knowledge", repoOrderArtificial, "artificialDependencyList.json")      
    successorDict, _, _, _ = cleanOrderDict(repoOrder, repoOrderArtificial, provider)
    detectLoops(successorDict)
    topologicalSort(successorDict)

def getPartialOrderIncremental(resourceType, provider):
    repoOrder = json.load(open("../regoFiles/repoOrderDict.json", "r"))
    repoOrderArtificial = json.load(open("../regoFiles/repoOrderArtificialDict.json", "r"))
    if not os.path.exists(f"../folderFiles/folders_{resourceType}_knowledge"):
        return
    print("test", provider)
    repoOrder = aggregateRegoPartialOrder(f"../folderFiles/folders_{resourceType}_knowledge", repoOrder, "dependencyList.json")  
    repoOrderArtificial = aggregateRegoPartialOrder(f"../folderFiles/folders_{resourceType}_knowledge", repoOrderArtificial, "artificialDependencyList.json")      
    successorDict, _, _, _ = cleanOrderDict(repoOrder, repoOrderArtificial, provider)
    detectLoops(successorDict)
    topologicalSort(successorDict)
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource_name", help="the name of the resource we want to get")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    if "terraform-provider-" in str(args.resource_name):
        ### Usage example: time python3 -u regoMVPGetPartialOrder.py --resource_name terraform-provider-azurerm
        provider = str(args.resource_name).split("-")[-1]
        getPartialOrderAll(provider)
    else:
        ### Usage example: time python3 -u regoMVPGetPartialOrder.py --resource_name azurerm_application_gateway
        resourceType = str(args.resource_name)
        provider = str(args.resource_name).split("_")[0]
        getPartialOrderIncremental(resourceType, provider)