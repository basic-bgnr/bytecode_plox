from opcodes import OpCode
import LanguageConstants
from collections import defaultdict

class Chunk:
    def __init__(self):
        self.codes = []#container for code
       
        self.lines = []#for determining the souce of error

        self.constants = []
        # todo: implement the following for improving performance 
        self.constants = [LanguageConstants.TRUE, LanguageConstants.FALSE, LanguageConstants.NIL]#container for literal value
        self._constant_map = defaultdict(lambda : None, {constant: index for index, constant in enumerate(self.constants)})# key: constant, value: index,=> self.constants[self._constant_map[key]]


    def push(self, opcode, at_line):
        self.codes.append(opcode)
        self.lines.append(at_line)

    def pushOpCode(self, op_code, at_line):
        self.codes.append(op_code)
        self.lines.append(at_line)

    def pushOpCodes(self, op_code1, op_code2, at_line):
        self.pushOpCode(op_code1, at_line)
        self.pushOpCode(op_code2, at_line)

    def getCodesLength(self):
        return len(self.codes) # returns addressable index(this doesn't need subtraction, can be directly indexed)

    def pushOpCodeAt(self, op_code, index):
        self.codes[index] = op_code

    def codeAt(self, index):
        return self.codes[index]

    def constantAt(self, index):
        # print('index ', index)
        return self.constants[index]

    def lineAt(self, index):
        return self.lines[index]

    def makeConstant(self, constant):
        index = self._constant_map[constant]

        if  index is not None:
            # print('found in previous')
            # print(self.constants)
            return index
        # print('found not in previous')
        # print(f"{constant}")
        # print(f"{[str(c) for c in self.constants]}")
        return self.addConstant(constant)

    #add the constant without any checks
    def addConstant(self, constant):
        self.constants.append(constant)
        index = len(self.constants) - 1
        self._constant_map[constant] = index 
        return index

    def pushConstant(self, constant, at_line):
        #constant is not directly used as key, because it's a instantiated class which gives different value when instantiated
        #even for the same value, so direct value is used.
        # the following code prevent repeated value to be inserted in the constant table
        # if (constant == self.)
        # elif (constant.values not in self._constant_map.keys()):
        #     self.constants.append(constant)
        #     index = len(self.constants) - 1
        #     self._constant_map[constant.values] = index
        # else:
        #     index = self._constant_map[constant.values]
        # breakpoint()
        #this is a major source of error
       
        index = self.makeConstant(constant)
        self.pushOpCodes(OpCode.OP_LOAD_CONSTANT, index, at_line)
        
        return index

        # if any error, try the following
        # index = self.makeConstant(constant)
        # self.pushOpCodes(OpCode.OP_CONSTANT, index, at_line)      
        # return index

    def getNextIPLocation(self):
        return len(self.codes)

def test():
    
    from disassembler import Disassembler
    from vm import Vm

    byte_array = Chunk()
    #############################################################
    constant = 100;
    byte_array.pushConstant(constant, at_line = 1)
    #############################################################

    constant = 200;
    byte_array.pushConstant(constant, at_line = 1)
    #############################################################


    byte_array.push(OpCode.OP_ADD, at_line = 1)
    byte_array.push(OpCode.OP_RETURN, at_line = 1);


    print(Disassembler(byte_array).disassemble())


    vm = Vm(byte_array)

    print("vm result ", vm.run())
