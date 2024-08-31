import sys
sys.path.insert(0, '..')
import json
import argparse
import csv
from utils.utils import *
import knowledgeBaseConstruction.regoMVPGetKnowledgeBase as regoMVPGetKnowledgeBase

def interpolateOperators(csvFileName, interpolateFileName, classFileName):
    candidateRuleStringFile = open("../interpolateRules.txt", "a")
    csvFile = open(csvFileName, "r")
    interpolateFile = open(interpolateFileName, "w")
    classFile = open(classFileName, "w")
    csvReader = csv.reader(csvFile, delimiter=',')
    fields = ['Operator', 'Shape', 'Operand1', 'Operand2', 'Operand3', 'Operand4', 'Operand5', 'Operand6', 'Operand7', 'Operand8']
    csvWriter = csv.writer(interpolateFile)
    csvWriter.writerow(fields)
    
    resourceType = csvFileName[find_nth(csvFileName, "/", -2)+1:find_nth(csvFileName, "/", -1)]
    operationType = csvFileName[find_nth(csvFileName, "/", -1)+1:]
    with open('../regoFiles/repoView.json', 'r') as f:
        resourceView = json.load(f)
    classResult = defaultdict(list)
    
    for row in csvReader:
        if row[0] == "Operator":
            continue
        operationList = row[1].split("If")
        operationList = operationList[0].split("Then")
        print(operationList)
        rowIndex = 2
        newRowList = []
        newStringList = []
        if operationList[0] in ["Enum", "EnumComboUp", "EnumComboDown"]:
            statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1]
            resourceType = statement1.split(".")[0]
            resourceAttributes = ".".join(statement1.split(".")[1:])
            for attrValue in resourceView[resourceType][resourceAttributes]:
                newRowList.append([row[0], row[1].replace("EnumThen", "ConstantThen"), row[2].replace("Enum", str(attrValue))] + row[3:])
                newStringList.append(f"If the value of {statement1} is {attrValue}, ")
            rowIndex += 1
        elif  operationList[0] in ["Reference"]:
            resourceType1 = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
            resourceAttr1 = row[rowIndex][find_nth(row[rowIndex], ".", 1)+1:find_nth(row[rowIndex], "=", 1)-1]
            resourceType2 = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
            resourceAttr2 = row[rowIndex+1][find_nth(row[rowIndex+1], ".", 1)+1:find_nth(row[rowIndex+1], "=", 1)-1]
            newRowList.append(row)
            newStringList.append(f"If the value of {resourceType1}.{resourceAttr1} depends on {resourceType2}.{resourceAttr2}, ")
            rowIndex += 2
        else:
            continue
        if operationList[1] in ["CountChild", "CountParent", "CIDRMask", "CIDRMaskComboDown", "CIDRMaskComboUp"]:
            for newRow in newRowList:
                for index in range(len(newRow)):
                    #print("newRow:", newRow[index])
                    newRow[index] = newRow[index].replace("CountChild", "AggChild")
                    newRow[index] = newRow[index].replace("CountParent", "AggParent")
                    newRow[index] = newRow[index].replace("CIDRMask", "CIDRRange")
            for index in range(len(newStringList)):
                newString = newStringList[index]
                if operationList[1] in ["CountChild"]:
                    resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
                    resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
                    newString += f"then what is the maximum amount of {resourceA} that could depend on {resourceB}? Please answer with an integer"
                elif operationList[1] in ["CountParent"]:
                    resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
                    resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
                    newString += f"then what is the maximum amount of {resourceB} that could directly connect to {resourceA}? Please answer with an integer"
                elif operationList[1] in ["CIDRMask", "CIDRMaskComboDown", "CIDRMaskComboUp"]:
                    resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
                    statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1]
                    newString += f"then what is the maximum CIDR mask length {statement1} could use? Please answer with an integer"
                newStringList[index] = newString
        elif operationList[1] in ["Enum"]:
            statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1]
            resourceType = statement1.split(".")[0]
            resourceAttributes = ".".join(statement1.split(".")[1:])
            tempRowList = newRowList[:]
            newRowList = []
            for newRow in tempRowList:
                for attrValue in resourceView[resourceType][resourceAttributes]:
                    tempRow = newRow[:]
                    tempRow[1] = tempRow[1].replace("Enum", "NonConstant")
                    tempRow[3] = tempRow[3].replace("Enum", str(attrValue))
                    newRowList.append(tempRow)
            tempStringList = newStringList[:]
            newStringList = []
            for newString in tempStringList:
                for attrValue in resourceView[resourceType][resourceAttributes]:
                    tempString = newString
                    tempString += f"then the value of {statement1} cannot be {attrValue}? Please answer with True or False"
                    newStringList.append(tempString)
        else:
            continue
        for index in range(len(newRowList)):
            newRow = newRowList[index]
            newString = newStringList[index]
            csvWriter.writerow(newRow)
            classResult["####".join(row)].append(["####".join(newRow), newString, None])
            candidateRuleStringFile.write(newString+"\n")
    json.dump(classResult, classFile, sort_keys = True, indent = 4)
    csvFile.close()
    interpolateFile.close()
    classFile.close()

def fixInterpolation(classID):
    interpolationData = json.load(open(classID+"IN.json", "r"))
    clearedData = json.load(open(classID+"FICL.json", "r"))
    languageFormat = ""
    for key in sorted(list(interpolationData.keys())):
        for superKey in clearedData:
            for block in clearedData[superKey]:
                if block[0] == key:
                    languageFormat = block[1]
        interpolationData[key] = [languageFormat] + interpolationData[key]
        for block in interpolationData[key][1:]:
            if block[2] != None:
                ruleDetailList = block[0].split("####")
                if "ThenAggChild" in ruleDetailList[1]:
                    ruleDetailList[1] = ruleDetailList[1].replace("Enum", "Constant")
                    result1 = "####".join(ruleDetailList)
                    block[0] = result1
                elif "ThenAggParent" in ruleDetailList[1]:
                    ruleDetailList[1] = ruleDetailList[1].replace("Enum", "Constant")
                    result1 = "####".join(ruleDetailList)
                    block[0] = result1
    json.dump(interpolationData, open(classID+"IN.json", "w"), sort_keys = True, indent = 4)
    
def explainInterpolation(resourceType, classID): 
    interpolationData = json.load(open(classID+"IN.json", "r"))
    explainedData = []
    countTrue, countFalse = 0, 0
    for key in sorted(list(interpolationData.keys())):
        interpolationData[key] = interpolationData[key][1:]
        for block in interpolationData[key]:
            try:
                if block[2] != None and block[2] != "None" and block[2] != "null" and block[2] != "False" and block[2] != "false":
                    ruleDetailList = block[0].split("####")
                    if "ThenAggChild" in ruleDetailList[1]:
                        if not block[2].isnumeric():
                            countFalse += 1
                            continue
                        ruleDetailList[-2] = ruleDetailList[-2].replace("String", block[2])
                        ruleDetailList[1] = ruleDetailList[1].replace("Enum", "Constant")
                        result1 = "####".join(ruleDetailList)
                        result2 = block[1].split("?")[0].replace("what is the", "the") + f" is {block[2]}"
                    elif "ThenAggParent" in ruleDetailList[1]:
                        if not block[2].isnumeric():
                            countFalse += 1
                            continue
                        ruleDetailList[-1] = ruleDetailList[-1].replace("String", block[2])
                        ruleDetailList[1] = ruleDetailList[1].replace("Enum", "Constant")
                        result1 = "####".join(ruleDetailList)
                        result2 = block[1].split("?")[0].replace("what is the", "the") + f" is {block[2]}"
                    elif "ThenNonConstant" in ruleDetailList[1]:
                        if block[2] != "True" and block[2] != "true":
                            countFalse += 1
                            continue
                        ruleDetailList[-1] = ruleDetailList[-1].replace("String", "true")
                        ruleDetailList[-1] = ruleDetailList[-1].replace("True", "true")
                        ruleDetailList[-1] = ruleDetailList[-1].replace("False", "false")
                        ruleDetailList[-2] = ruleDetailList[-2].replace("True", "true")
                        ruleDetailList[-2] = ruleDetailList[-2].replace("False", "false")
                        result1 = "####".join(ruleDetailList)
                        result2 = block[1].split("?")[0]
                    elif "ThenCIDRRange" in ruleDetailList[1]:
                        if not block[2].isnumeric():
                            countFalse += 1
                            continue
                        ruleDetailList[-1] = ruleDetailList[-1].replace("CIDR", block[2])
                        result1 = "####".join(ruleDetailList)
                        result2 = block[1].split("?")[0].replace("what is the", "the") + f" is {block[2]}"
                    block[0], block[1] = result1, result2
                    explainedData.append([resourceType, ",".join(block[0].split("####")), result2])
                    countTrue += 1
                else:
                    countFalse += 1
            except:
                print("Something went wrong during interpolation result explain phase")
    json.dump(explainedData, open(classID+"FIIN.json", "w"), sort_keys = True, indent = 4)
    return explainedData, countTrue, countFalse
   
if __name__ == "__main__":
    ### Usage example: python3 regoMVPRuleInterpolate.py
    allExplainedData = []
    allCountTrue, allCountFalse = 0, 0
    for resourceName in regoMVPGetKnowledgeBase.resourceList:
        for operator in ["ATTR", "COMBO", "TOPO"]:
            #fixInterpolation(f"../ruleJsonFiles/{resourceName}/{operator}")
            #fixInterpolation(f"../ruleJsonFiles/{resourceName}/{operator}RE")
            explainedData1, countTrue1, countFalse1 = explainInterpolation(resourceName, f"../interpolationFiles/{resourceName}/{operator}")
            explainedData2, countTrue2, countFalse2 = explainInterpolation(resourceName, f"../interpolationFiles/{resourceName}/{operator}RE")
            allExplainedData += explainedData1 + explainedData2
            allCountTrue += countTrue1 + countTrue2
            allCountFalse += countFalse1 + countFalse2
    json.dump(allExplainedData, open("../testFiles/interpolationCandidate.json", "w"), sort_keys = True, indent = 4)
    print("Count True: ", allCountTrue, "Count False: ", allCountFalse)