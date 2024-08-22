### Main entry for summarizing the results of each validation iteration. E.g.
### which set of checks forms an indistich check set and must be considered together.
import json
import os
from collections import defaultdict
from SMTPipeline import *

class DisjSet:
    def __init__(self, n):
        self.rank = [1] * n
        self.parent = [i for i in range(n)]
 
    def find(self, x):
        if (self.parent[x] != x):
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def Union(self, x, y):    
        xset = self.find(x)
        yset = self.find(y) 
        if xset == yset:
            return

        if self.rank[xset] < self.rank[yset]:
            self.parent[xset] = yset
 
        elif self.rank[xset] > self.rank[yset]:
            self.parent[yset] = xset

        else:
            self.parent[yset] = xset
            self.rank[xset] = self.rank[xset] + 1
            
### Please use summarizeConflictResolveValidationResult instead for true positive validation
def summarizeTruePositiveValidationResult(iteration):
    orderList = json.load(open("../regoFiles/orderList.json", "r"))
    validatedList = []
    candidateList = []
    completeList = []
    countTotal = 0
    for resourceType in orderList:
        for round in range(1,iteration+1):
            validationDirectory = f"../testFiles/validationFolders_{round}_true/{resourceType}"
            if not os.path.exists(validationDirectory):
                continue
            for jsonFileName in sorted(list(os.listdir(validationDirectory))):
                jsonPath = os.path.join(validationDirectory, jsonFileName)
                fr = open(f"{jsonPath}", "r")
                finalResult = json.load(fr)
                if finalResult[4] == False:
                    if finalResult[5] == 1:
                        validatedList.append([resourceType, ",".join(finalResult[0])])
                        print(resourceType, finalResult[4], finalResult[5], ",".join(finalResult[0]), jsonFileName)
                fr.close()
                countTotal += 1
    
    validatedFile = open(f"../testFiles/validatedFile{iteration}.json", "w")
    json.dump(validatedList, validatedFile, sort_keys = True, indent = 4)
    validatedFile.close()
    candidateList = []
    
    completeFile = open(f"../testFiles/completeFile{iteration}.json", "r")
    completeList = json.load(completeFile)
    
    for item in completeList:
        if item not in validatedList:
            candidateList.append(item)
    candidateFile = open(f"../testFiles/candidateFile{iteration}.json", "w")
    json.dump(candidateList, candidateFile, sort_keys = True, indent = 4)
    candidateFile.close()
    

def summarizeFalsePositiveRemovalResult(iteration):
    orderList = json.load(open("../regoFiles/orderList.json", "r"))
    candidateFile = open(f"../testFiles/candidateFile{iteration}.json", "r")
    candidateList = json.load(candidateFile)
    countTotal = 0
    countTrue = 0
    partialList = []
    for resourceType in orderList:
        validationDirectory1 = f"../testFiles/validationFolders_{iteration}_overlap_false/{resourceType}"
        for validationDirectory in [validationDirectory1]:
            if not os.path.exists(validationDirectory):
                continue
            for jsonFileName in sorted(list(os.listdir(validationDirectory))):
                jsonPath = os.path.join(validationDirectory, jsonFileName)
                fr = open(f"{jsonPath}", "r")
                finalResult = json.load(fr)
                if finalResult[4] == False:
                    partialList.append([resourceType, ",".join(finalResult[0])])
                    print(resourceType, finalResult[4], finalResult[5], ",".join(finalResult[0]), jsonFileName)
                else:
                    countTrue += 1
                fr.close()
                countTotal += 1
                
    newCompleteList = []
    for item in candidateList:
        if item in partialList:
            newCompleteList.append(item)
    
    print("Length of partial list: ", len(partialList))
    print("Difference is: ", len(candidateList)-len(newCompleteList), countTrue, len(candidateList), len(partialList), len(newCompleteList))
    
    newIteration = iteration+1
    completeFile = open(f"../testFiles/completeFile{newIteration}.json", "w")
    json.dump(newCompleteList, completeFile, sort_keys = True, indent = 4)
    completeFile.close()

def summarizeInterpolationResult(iteration):
    orderList = json.load(open("../regoFiles/orderList.json", "r"))
    validatedFile = open(f"../testFiles/interValidatedFile{iteration}.json", "r")
    validatedList = json.load(validatedFile)
    countTotal = 0
    countTrue = 0
    partialList = []
    for resourceType in orderList:
        validationDirectory1 = f"../testFiles/validationFolders_{iteration}_inter_true/{resourceType}"
        for validationDirectory in [validationDirectory1]:
            if not os.path.exists(validationDirectory):
                continue
            for jsonFileName in sorted(list(os.listdir(validationDirectory))):
                jsonPath = os.path.join(validationDirectory, jsonFileName)
                fr = open(f"{jsonPath}", "r")
                finalResult = json.load(fr)
                if finalResult[4] == False:
                    partialList.append([resourceType, ",".join(finalResult[0])])
                    print(resourceType, finalResult[4], finalResult[5], ",".join(finalResult[0]), jsonFileName)
                else:
                    countTrue += 1
                fr.close()
                countTotal += 1
                
    print("Length of partial list: ", len(partialList))
    validatedList += partialList
    completeFile = open(f"../testFiles/validationProduct{iteration}.json", "w")
    json.dump(validatedList, completeFile, sort_keys = True, indent = 4)
    completeFile.close()
            
def summarizeConflictResolveValidationResult(iteration):
    orderList = json.load(open("../regoFiles/orderList.json", "r"))
    validatedList = []
    countTotal = 0
    ruleDict = defaultdict()
    ruleList =[]
    ruleTypeDict = defaultdict()
    for resourceType in orderList:
        validationDirectory = f"../testFiles/validationFolders_{iteration}_overlap_true/{resourceType}"
        if not os.path.exists(validationDirectory):
            continue
        for jsonFileName in sorted(list(os.listdir(validationDirectory))):
            jsonPath = os.path.join(validationDirectory, jsonFileName)
            fr = open(f"{jsonPath}", "r")
            finalResult = json.load(fr)
            if len(finalResult) == 7 and len(finalResult[6]) >= 1 and finalResult[4] == False:
                ruleDict[",".join(finalResult[0])] = []
                for tempRule in finalResult[6]:
                    ruleDict[",".join(finalResult[0])].append(",".join(tempRule))
                ruleList.append(",".join(finalResult[0]))
                ruleTypeDict[",".join(finalResult[0])] = resourceType
                print(resourceType, len(finalResult[6]), ",".join(finalResult[0]), jsonFileName)
            fr.close()
            countTotal += 1
        
    obj = DisjSet(10000)           
    for index1, rule1 in enumerate(ruleList):
        for rule2 in ruleDict[rule1]:
            if rule1 == rule2:
                continue
            if rule2 in ruleDict and rule1 in ruleDict[rule2]:
                for index2, tempRule in enumerate(ruleList):
                    if rule2 == tempRule and index1 < index2:
                        obj.Union(index1, index2)
    
    disjointSetUnion = defaultdict(list)
    for index1, rule1 in enumerate(ruleList):
        disjointSetUnion[obj.find(index1)].append(index1) 
    overlapTestDict = defaultdict(list)
    for ruleIndex in disjointSetUnion:
        tempRuleSet = set()
        if len(disjointSetUnion[ruleIndex]) > 1:
            overlapTestDict[ruleList[ruleIndex]] = []
        for otherRuleIndex in disjointSetUnion[ruleIndex]:
            tempRuleSet.add(ruleList[otherRuleIndex])
            if len(disjointSetUnion[ruleIndex]) > 1:
                overlapTestDict[ruleList[ruleIndex]].append([ruleTypeDict[ruleList[otherRuleIndex]],ruleList[otherRuleIndex]])
    
    arglists = []
    try:
        interpolationDataList = json.load(open(f"../testFiles/interpolationCandidate.json", "r"))
    except:
        interpolationDataList = []
    ruleDataList = json.load(open(f"../testFiles/completeFile{iteration}.json", "r"))
    for key in overlapTestDict:
        for index in range(len(overlapTestDict[key])):
            targetRule = overlapTestDict[key][index][1]
            print("Target checks:", targetRule)
            otherRuleList = overlapTestDict[key][:index] + overlapTestDict[key][index+1:]
            for otherRule in otherRuleList:
                print("Other checks:", otherRule)
            arglists.append([[ruleTypeDict[targetRule], 'I', targetRule], otherRuleList, ruleDataList, interpolationDataList, False, iteration, True, False])
            #coreValidationPipeline([ruleTypeDict[targetRule], 'I', targetRule], otherRuleList, ruleDataList, interpolationDataList, False, iteration, True, False)
    pool = multiprocessing.Pool(processes=12)
    for arglist in arglists:
        pool.apply_async(coreValidationPipeline, args=arglist)
    pool.close()
    pool.join()
    
    InEquivalentClassDict = defaultdict()
    for resourceType in orderList:
        resolveDirectory = f"../testFiles/validationFolders_{iteration}_overlap_resolve/{resourceType}"
        if not os.path.exists(resolveDirectory):
            continue
        for jsonFileName in sorted(list(os.listdir(resolveDirectory))):
            jsonPath = os.path.join(resolveDirectory, jsonFileName)
            fr = open(f"{jsonPath}", "r")
            finalResult = json.load(fr)
            if finalResult[4] == True:
                testRule = ",".join(finalResult[0])
                for index in range(len(ruleList)):
                    if ruleList[index] == testRule:
                        ruleIndex = index
                InEquivalentClassDict[obj.find(ruleIndex)] = True
    print("InEquivalentClassDict:", InEquivalentClassDict)
    totalOverlaps = 0
    totalImpacted = 0
    
    validatedPrevList = []
    if iteration >= 1:
        prevIteration = iteration - 1
        validatedPrevFile = open(f"../testFiles/validatedFile{prevIteration}.json", "r")
        validatedPrevList = json.load(validatedPrevFile)
    print("Length of previous validated list: ", len(validatedPrevList))
    
    for ruleIndex in range(len(ruleList)):
        print(ruleIndex, disjointSetUnion[obj.find(ruleIndex)])
        tempRuleSet = set()
        if obj.find(ruleIndex) in InEquivalentClassDict:
            print("Inequivalent!", ruleList[ruleIndex])
            continue
        for otherRuleIndex in disjointSetUnion[obj.find(ruleIndex)]:
            print(otherRuleIndex, ruleList[otherRuleIndex])
            tempRuleSet.add(ruleList[otherRuleIndex])
        onlyFlag = True
        for otherRule in ruleDict[ruleList[ruleIndex]]:
            if otherRule not in tempRuleSet:
                onlyFlag = False
        if onlyFlag == True:
            if [ruleTypeDict[ruleList[ruleIndex]],ruleList[ruleIndex]] not in validatedPrevList:
                if obj.find(ruleIndex) != ruleIndex:
                    totalOverlaps += 1
                if obj.find(ruleIndex) == ruleIndex:
                    if len(disjointSetUnion[obj.find(ruleIndex)]) > 1:
                        totalImpacted += len(disjointSetUnion[obj.find(ruleIndex)])
                validatedList.append([ruleTypeDict[ruleList[ruleIndex]],ruleList[ruleIndex]])
    print("Total amount of equivalent rules: ", totalOverlaps, totalImpacted)
    validatedList = validatedPrevList + validatedList
    print("Length of new validated list: ", len(validatedList))
    
    validatedFile = open(f"../testFiles/validatedFile{iteration}.json", "w")
    json.dump(validatedList, validatedFile, sort_keys = True, indent = 4)
    validatedFile.close()
    candidateList = []
    
    completeFile = open(f"../testFiles/completeFile{iteration}.json", "r")
    completeList = json.load(completeFile)
    
    for item in completeList:
        if item not in validatedList:
            candidateList.append(item)
    candidateFile = open(f"../testFiles/candidateFile{iteration}.json", "w")
    json.dump(candidateList, candidateFile, sort_keys = True, indent = 4)
    candidateFile.close()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--control_index", help="current iteration identifier")
    parser.add_argument("--direction", help="true positive validation or false positive removal")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    if str(args.direction) == "True":
        summarizeConflictResolveValidationResult(int(args.control_index))
    else:
        summarizeFalsePositiveRemovalResult(int(args.control_index))
