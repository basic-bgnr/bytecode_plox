from opcodes import OpCode

class Vm:
    def __init__(self, chunk):
        self.chunk = chunk
        self.stack = []
        self.ip = 0


    def run(self):
        while current_op_code := self.getOpCode():

            if (current_op_code == OpCode.OP_RETURN):
                return self.stack.pop()

            elif (current_op_code == OpCode.OP_CONSTANT):
                self.pushStack(self.loadConstant())

            elif (current_op_code == OpCode.OP_ADD):
                op1 = self.popStack()
                op2 = self.popStack()

                self.pushStack(op1 + op2)

            elif (current_op_code == OpCode.OP_SUB):
                op1 = self.popStack()
                op2 = self.popStack() 

                self.pushStack(op1 - op2)

            elif (current_op_code == OpCode.OP_MUL):
                op1 = self.popStack()
                op2 = self.popStack()

                self.pushStack(op1 * op2)

            elif (current_op_code == OpCode.OP_DIV):
                op1 = self.popStack() 
                op2 = self.popStack()

                self.pushStack(op1 / op2)

            elif (current_op_code == OpCode.OP_NEG):
                op1 = self.popStack()
                self.pushStack(-op1)
        
        print('computed ', self.stack)

    def getOpCode(self):
        if (not self.isAtEnd()):
            ret_value = self.chunk.codeAt(self.ip)
            self.advance()
            return ret_value
        return None

    def isAtEnd(self):
        return len(self.chunk.codes) <= self.ip

    def advance(self):
        self.ip += 1

    def loadConstant(self):
        index = self.getOpCode()
        return self.chunk.constantAt(index)

    def popStack(self):
        # print('popping ', self.stack)
        return self.stack.pop()

    def pushStack(self, value):
        # print('pushing ', self.stack)
        self.stack.append(value)
