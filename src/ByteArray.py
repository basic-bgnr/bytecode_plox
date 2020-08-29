from opcodes import OpCode
import LanguageConstants
from collections import defaultdict

class Chunk:
    def __init__(self):
        self.codes = []#container for code
       
        self.lines = []#for determining the souce of error

        self.constants = [LanguageConstants.TRUE, LanguageConstants.FALSE, LanguageConstants.NIL]#container for literal value
        self._constant_map = defaultdict(lambda : None, {constant: index for index, constant in enumerate(self.constants)})# key: constant, value: index,=> self.constants[self._constant_map[key]]


    def push(self, opcode, at_line):
        self.codes.append(opcode)
        self.lines.append(at_line)

    def codeAt(self, index):
        return self.codes[index]

    def constantAt(self, index):
        return self.constants[index]

    def lineAt(self, index):
        return self.lines[index]

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
        if (self._constant_map[constant] is not None): #check if nil, true, false is supplied
            index = self._constant_map[constant]
            
        elif(self._constant_map[constant.value] is not None):
            index = self._constant_map[constant.value] 
        else:
            self.constants.append(constant)
            index = len(self.constants) - 1
            self._constant_map[constant.value] = index


        self.push(opcode=OpCode.OP_CONSTANT, at_line = at_line)
        self.push(opcode=index, at_line = at_line)
        
        return index




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
