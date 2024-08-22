### Definition of check and operand formats.
class Operand:
    def __init__(self, operandResource, operandAttribute, operandType):
        self.operandResource = operandResource
        self.operandAttribute = operandAttribute
        self.operandType = operandType
    def __str__(self):
        return f"{self.operandResource}.{self.operandAttribute} == {self.operandType}"
        #return f"{self.operandResource}, {self.operandAttribute}, {self.operandType}"
        
class Rule:
    def __init__(self, operator, ruleID):
        self.operator = operator
        self.shape = None
        self.operand1 = None
        self.operand2 = None
        self.operand3 = None
        self.operand4 = None
        self.operand5 = None
        self.operand6 = None
        self.operand7 = None
        self.operand8 = None
        self.constructed = False
        self.retrieved = False
        self.obtained = False
        self.ruleID = ruleID
        
    def __str__(self):
        result = self.operator + "\n"
        if (self.operand1 != None):
            result += str(self.operand1) + "\n"
        if (self.operand2 != None):
            result += str(self.operand2) + "\n"
        if (self.operand3 != None):
            result += str(self.operand3) + "\n"
        if (self.operand4 != None):
            result += str(self.operand4)
        if (self.operand5 != None):
            result += str(self.operand5) + "\n"
        if (self.operand6 != None):
            result += str(self.operand6)
        if (self.operand7 != None):
            result += str(self.operand7) + "\n"
        if (self.operand8 != None):
            result += str(self.operand8)
        return result
    
    def initiate(self, arguments):
        if len(arguments) >= 1:
            self.shape = arguments[0][0]
        if len(arguments) >= 2:
            self.operand1 = Operand(arguments[1][0], arguments[1][1], arguments[1][2])
        if len(arguments) >= 3:
            self.operand2 = Operand(arguments[2][0], arguments[2][1], arguments[2][2])
        if len(arguments) >= 4:
            self.operand3 = Operand(arguments[3][0], arguments[3][1], arguments[3][2])
        if len(arguments) >= 5:
            self.operand4 = Operand(arguments[4][0], arguments[4][1], arguments[4][2])
        if len(arguments) >= 6:
            self.operand5 = Operand(arguments[5][0], arguments[5][1], arguments[5][2])
        if len(arguments) >= 7:
            self.operand6 = Operand(arguments[6][0], arguments[6][1], arguments[6][2])
        if len(arguments) >= 8:
            self.operand7 = Operand(arguments[7][0], arguments[7][1], arguments[7][2])
        if len(arguments) >= 9:
            self.operand8 = Operand(arguments[8][0], arguments[8][1], arguments[8][2])
    