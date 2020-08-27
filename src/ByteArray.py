from opcodes import OpCode
class Chunk:
    def __init__(self):
        self.codes = []#container for code
        self.constants = []#container for literal value
        self.lines = []#for determining the souce of error

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
        self.constants.append(constant)
        index = len(self.constants) - 1

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
