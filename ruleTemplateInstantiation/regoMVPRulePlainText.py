import sys
sys.path.insert(0, '..')
import csv
from collections import defaultdict
import argparse
from utils.utils import *
import json

def normalOperationTranslation(operation, row, rowIndex, resultStringList, operationList):
    resourceA, resourceB, resourceC, resourceD, resourceE = "", "", "", "", ""
    statement1, statement2, statement3, statement4, statement5 = "", "", "", "", ""
    if operation == "Reference":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"{statement1} depends on {statement2}")
        rowIndex += 2
    elif operation == "Negation":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1]
        resultStringList.append(f"{statement1} is null (i.e. it does not refer to {statement2})")
        rowIndex += 2
    elif operation == "Associate":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+2][:find_nth(row[rowIndex+2], ".", 1)] + ".b"
        resourceC = row[rowIndex+3][:find_nth(row[rowIndex+3], ".", 1)] + ".c"
        if  row[rowIndex+2] == row[rowIndex+3]:
            resultStringList.append(f"both {resourceB} and {resourceC} are directly connected to {resourceA}")
        else:
            resultStringList.append(f"{resourceB} and {resourceC} connected or associated with each other via {resourceA}")
        rowIndex += 4
    elif operation == "Branch":
        if operationList[0] in ["Associate"] and operationList[1] in ["Branch", "AncestorBranch"]:
            resourceB = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".b"
            resourceC = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".c"
            statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceB[:-2], resourceB)
            statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceC[:-2], resourceC)
            resourceD = row[rowIndex+2][:find_nth(row[rowIndex+2], ".", 1)] + ".d"
            resultStringList.append(f"both {statement1} and {statement2} depends on {resourceD}")
        else:
            resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
            resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
            statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
            statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceB[:-2], resourceB)
            resourceC = row[rowIndex+2][:find_nth(row[rowIndex+2], ".", 1)] + ".c"
            resultStringList.append(f"both {statement1} and {statement2} depends on {resourceC}")
        rowIndex += 4
    elif operation == "CountParent":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        resultStringList.append(f"the number of {resourceB} that {resourceA} could depend on is restricted to certain value")
        rowIndex += 2   
    elif operation == "CountChild":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        resultStringList.append(f"the number of {resourceA} that could depend on {resourceB} is restricted to certain value")
        rowIndex += 2
    elif operation == "ConflictChild":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        typeA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        if rowIndex == 2:
            resultStringList.append(f"{resourceA} is the only {typeA} that directly depends on {resourceB}")
        else:
            resultStringList.append(f"{resourceB} could only have a single {typeA} that is {resourceA}")
        rowIndex += 2
    elif operation == "Exclusive":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        resultStringList.append(f"{resourceA} is the only resource that directly depends on {resourceB}")
        rowIndex += 2
    elif operation == "Intra":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        resourceC = row[rowIndex+2][:find_nth(row[rowIndex+2], ".", 1)] + ".c"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"both {statement1} and {statement2} depends on {resourceC}")
        rowIndex += 4
    elif operation == "Equal":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"{statement1} == {statement2}")
        rowIndex += 2
    elif operation == "EqualCombo":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"{statement1} == {statement2}")
        rowIndex += 2
    elif operation == "Unequal":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"{statement1} != {statement2}")
        rowIndex += 2
    elif operation == "UnequalCombo":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"{statement1} != {statement2}")
        rowIndex += 2
    elif operation == "CIDRInclude":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"the CIDR range of {statement2} contains the CIDR range of {statement1}")
        rowIndex += 2
    elif operation == "CIDRIncludeCombo":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"the CIDR range of {statement2} contains the CIDR range of {statement1}")
        rowIndex += 2
    elif operation == "CIDRExclude":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"the CIDR range of {statement2} does not overlap with the CIDR range of {statement1}")
        rowIndex += 2
    elif operation == "CIDRExcludeCombo":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:find_nth(row[rowIndex+1], "=", 1)-1].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"the CIDR range of {statement2} does not overlap with the CIDR range of {statement1}")
        rowIndex += 2
    elif operation == "Absence":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"{statement1} is null or empty")
        rowIndex += 1
    elif operation == "AbsenceComboDown":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"{statement1} is null or empty")
        rowIndex += 1
    elif operation == "AbsenceComboUp":
        resourceB = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".b"
        statement2 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"{statement2} is null or empty")
        rowIndex += 1
    elif operation == "Existence":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"{statement1} is not null nor empty")
        rowIndex += 1
    elif operation == "ExistenceComboDown":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"{statement1} is not null nor empty")
        rowIndex += 1
    elif operation == "ExistenceComboUp":
        resourceB = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".b"
        statement2 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"{statement2} is not null nor empty")
        rowIndex += 1
    elif operation == "Constant":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"there is {statement1}")
        rowIndex += 1
    elif operation == "ConstantComboDown":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"there is {statement1}")
        rowIndex += 1
    elif operation == "ConstantComboUp":
        resourceB = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".b"
        statement2 = row[rowIndex][:].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"there is {statement2}")
        rowIndex += 1
    elif operation == "NonConstant":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"there cannot be {statement1}")
        rowIndex += 1
    elif operation == "NonConstantComboDown":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"there cannot be {statement1}")
        rowIndex += 1
    elif operation == "NonConstantComboUp":
        resourceB = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".b"
        statement2 = row[rowIndex][:].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"there cannot be {statement2}")
        rowIndex += 1
    elif operation == "CIDRRange":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resultStringList.append(f"{statement1} range cannot be smaller than {statement2}")
        rowIndex += 1
    elif operation == "CIDRRangeComboDown":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resultStringList.append(f"{statement1} range cannot be smaller than {statement2}")
        rowIndex += 1
    elif operation == "CIDRRangeComboUp":
        resourceB = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".b"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceB[:-2], resourceB)
        statement2 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resultStringList.append(f"{statement1} range cannot be smaller than {statement2}")
        rowIndex += 1
    elif operation == "AggParent":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)]
        statement2 = row[rowIndex+1][find_nth(row[rowIndex+1], "=", 2)+2:]
        resultStringList.append(f"the number of {resourceB} that {resourceA} could depend on is restricted to {statement2}")
        rowIndex += 1
    elif operation == "AggChild":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        statement1 = row[rowIndex][find_nth(row[rowIndex], "=", 2)+2:]
        resultStringList.append(f"the number of {resourceA} that could depend on {resourceB} is restricted to {statement1}")
        rowIndex += 2
    elif operation == "Enum":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        if rowIndex == 2:
            resultStringList.append(f"{statement1} is of certain value")
        else:
            resultStringList.append(f"{statement1} cannot use certain value")
        rowIndex += 1
    elif operation == "EnumComboDown":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        if rowIndex == 2:
            resultStringList.append(f"{statement1} is of certain value")
        else:
            resultStringList.append(f"{statement1} cannot use certain value")
        rowIndex += 1
    elif operation == "EnumComboUp":
        resourceB = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".b"
        statement2 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceB[:-2], resourceB)
        if rowIndex == 2:
            resultStringList.append(f"{statement2} is of certain value")
        else:
            resultStringList.append(f"{statement2} cannot use certain value")
        rowIndex += 1
    elif operation == "CIDRMask":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"{statement1} has certain CIDR mask length restrictions")
        rowIndex += 1
    elif operation == "CIDRMaskComboDown":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        statement1 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceA[:-2], resourceA)
        resultStringList.append(f"{statement1} has certain CIDR mask length restrictions")
        rowIndex += 1
    elif operation == "CIDRMaskComboUp":
        resourceB = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".b"
        statement2 = row[rowIndex][:find_nth(row[rowIndex], "=", 1)-1].replace(resourceB[:-2], resourceB)
        resultStringList.append(f"{statement2} has certain CIDR mask length restrictions")
        rowIndex += 1
    elif operation == "AncestorReference":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        resultStringList.append(f"{resourceA} has an ancestor resource {resourceB}")
        rowIndex += 2
    elif operation == "AncestorConflictChild":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        typeA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)]
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        if rowIndex == 2:
            resultStringList.append(f"{resourceA} is the only {typeA} under {resourceB}")
        else:
            resultStringList.append(f"{resourceB} could only contain a single {typeA} resource that is {resourceA}")
        rowIndex += 2
    elif operation == "Peer":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        resultStringList.append(f"{resourceA} peered or connected with {resourceB}")
        rowIndex += 2
    elif operation == "AncestorAssociate":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+2][:find_nth(row[rowIndex+2], ".", 1)] + ".b"
        resourceC = row[rowIndex+3][:find_nth(row[rowIndex+3], ".", 1)] + ".c"
        resultStringList.append(f"{resourceB} and {resourceC} connected or associated with each other via {resourceA}")
        rowIndex += 4
    elif operation == "AncestorBranch":
        if operationList[0] in ["Associate"] and operationList[1] in ["Branch", "AncestorBranch"]:
            resourceB = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".b"
            resourceC = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".c"
            resourceD = row[rowIndex+2][:find_nth(row[rowIndex+2], ".", 1)] + ".d"
            resultStringList.append(f"some {resourceD} has both {resourceB} and {resourceC}")
        else:
            resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
            resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
            resourceC = row[rowIndex+2][:find_nth(row[rowIndex+2], ".", 1)] + ".c"
            resultStringList.append(f"some {resourceC} has both {resourceA} and {resourceB}")
        rowIndex += 4
    elif operation == "BinConstantCombo":
        resourceA = row[rowIndex][:find_nth(row[rowIndex], ".", 1)] + ".a"
        resourceB = row[rowIndex+1][:find_nth(row[rowIndex+1], ".", 1)] + ".b"
        statement1 = row[rowIndex][:].replace(resourceA[:-2], resourceA)
        statement2 = row[rowIndex+1][:].replace(resourceB[:-2], resourceB)
        if rowIndex == 2:
            resultStringList.append(f"{statement1} and {statement2}")
        else:
            resultStringList.append(f"if {statement1} then {statement2}")
        rowIndex += 2
    
    return rowIndex
 
def reverseRuleExpression(csvFileName, csvReversedFileName):
    csvFile = open(csvFileName, "r")
    csvReversedFile = open(csvReversedFileName, "w")
    fields = ['Operator', 'Shape', 'Operand1', 'Operand2', 'Operand3', 'Operand4', 'Operand5', 'Operand6', 'Operand7', 'Operand8']
    csvWriter = csv.writer(csvReversedFile)
    csvWriter.writerow(fields)
    csvReader = csv.reader(csvFile, delimiter=',')
    
    for row in csvReader:
        if row[0] == "Operator":
            continue
        operationList = row[1].split("If")
        operationList = operationList[0].split("Then")
        if operationList[0] in ["AncestorReference", "AncestorConflictChild", "Peer", "AncestorAssociate", "AncestorBranch", "Enum", \
                                "Intra", "ConflictChild", "Associate", "Branch"]:
            continue
        if operationList[1] in ["BinConstantCombo", "EqualCombo", "UnequalCombo"]:
            continue
        if operationList[0] in ["Reference", "AncestorReference"] and operationList[1] in ["Branch", "AncestorBranch", "Associate", "AncestorAssociate", "Intra"]:
            continue
        print(operationList)
        rowIndex = 2
        resultStringList = []
        rowIndexList = [rowIndex]
        for operation in operationList:
            rowIndex = normalOperationTranslation(operation, row, rowIndex, resultStringList, operationList)
            rowIndexList.append(rowIndex)
        newRow = [row[0], "Then".join(operationList[::-1])]
        newRowIndexList = rowIndexList[::-1]
        for ele in range(len(newRowIndexList)-1):
            newRow += row[newRowIndexList[ele+1]:newRowIndexList[ele]]
        csvWriter.writerow(newRow)
    csvFile.close()
    csvReversedFile.close()


def translateCSVtoFormats(csvFileName, resultFileName, classFileName, candidateFileName = ""):
    
    candidateRuleStringFile = open("/vagrant/candidateRules.txt", "a")
    csvFile = open(csvFileName, "r")
    resultFile = open(resultFileName, "w")
    classFile = open(classFileName, "w")
    classResult = defaultdict(list)
    csvReader = csv.reader(csvFile, delimiter=',')
    
    resourceType = csvFileName[find_nth(csvFileName, "/", -2)+1:find_nth(csvFileName, "/", -1)]
    operationType = csvFileName[find_nth(csvFileName, "/", -1)+1:]
    print(resourceType, operationType)
    completeString = ""
    if candidateFileName != "":
        try:
            candidateData = json.load(open(candidateFileName, "r"))
        except:
            candidateData = []
    for row in csvReader:
        if row[0] == "Operator":
            continue
        if candidateFileName != "":
            if [resourceType, ",".join(row)] not in candidateData:
                candidateData.append([resourceType, ",".join(row)])
        operationList = row[1].split("If")
        operationList = operationList[0].split("Then")
        print(operationList)
        rowIndex = 2
        resultStringList = []
        rowIndexList = [rowIndex]
        for operation in operationList:
            rowIndex = normalOperationTranslation(operation, row, rowIndex, resultStringList, operationList)
            rowIndexList.append(rowIndex)
        
        index1, index2 = (len(rowIndexList)-2), (len(rowIndexList)-1)
        classKey = operationList[-1] + "####" + "####".join(row[rowIndexList[index1]:rowIndexList[index2]])
        classResult[classKey].append(["####".join(row)])
        
        resultString = ""
        for index in range(len(resultStringList)):
            if index == 0:
                resultString += "If "
            elif index == len(resultStringList)-1:
                resultString += ", Then "
            else:
                resultString += ", Then if "
            resultString += resultStringList[index]
        classResult[classKey][-1].append(resultString)
        classResult[classKey][-1].append(None)
        if resultString == "":
            print("Something went wrong when generating natural language description")
        completeString += resultString + "\n"
    
    json.dump(classResult, classFile, sort_keys = True, indent = 4)
    if candidateFileName != "":
        print(candidateData)
        json.dump(candidateData, open(candidateFileName, "w"), sort_keys = True, indent = 4)
    resultFile.write(completeString)
    candidateRuleStringFile.write(completeString)
    csvFile.close()
    resultFile.close()
    classFile.close()
    candidateRuleStringFile.close()
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_file", help="the name of csv file to be translated")
    parser.add_argument("--txt_file", help="the name of txt file for the output")
    parser.add_argument("--json_file", help="the name of json file for the output")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    ###  python3 regoMVPRulePlainText.py --csv_file /vagrant/csvFiles/azurerm_linux_virtual_machine/ATTR.csv --txt_file /vagrant/plainTextRules.txt --json_file /vagrant/ruleFiles/temp.json > outputTemp
    args = parse_args()
    translateCSVtoFormats(str(args.csv_file), str(args.txt_file), str(args.json_file))
     
