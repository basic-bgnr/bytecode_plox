from opcodes import OpCode
from values import MasterData, LanguageTypes
#Note: The vm's ip counter always points at the next instruction to execute
class Vm:
    def __init__(self, chunk=None):
        self.chunk = chunk
        self.stack = [] # constainer for MasterData
        self.ip = 0

        self.esp = 0
        self.ebp = 0

        self.table = {} #storing reference to

    def reportVMError(self, message):
        raise Exception(f"VM ERROR\n{message}\nAt line: {self.getCurrentInstructionLine()}")

    def reportError(self, message):
        raise Exception(f"{message}\nAt line: {self.getCurrentInstructionLine()}")

    def assertTypeEquality(self, op1, op2):
        if (op1.tipe == op2.tipe):
            return
        #op1.tipe.name, here .name can be called on `Enum` types to print their actual name
        self.reportError(f"type mismatch between the following:\n1. {op1}\n2. {op2}\nExpecting type: {op1.tipe.name}\nFound type: {op2.tipe.name}")

    def assertType(self, op1, tipe):
        if (op1.tipe == tipe):
            return
        self.reportError(f"operation can't be performed on: \n{op1}\nExpecting type: {tipe.name}\nFound type: {op1.tipe.name}")

    def assertOptionalTypes(self, op1, *tipes):
        if (op1.tipe in tipes):
            return
        self.reportError(f"operation can't be performed on:{op1.tipe.name}\nExpecting one of [{','.join([tipe.name for tipe in tipes])}] types")

    def run(self, chunk=None, start_at=0):
        if chunk is not None:
            self.chunk = chunk
            self.ip = start_at

        while current_op_code := self.getOpCode():

            if (current_op_code == OpCode.OP_RETURN):
                return self.popStack()

            elif (current_op_code == OpCode.OP_LOAD_CONSTANT):
                self.pushStack(self.loadConstant())

            elif (current_op_code == OpCode.OP_ADD):
                op1 = self.popStack() #MasterData
                op2 = self.popStack() #MasterData

                self.assertOptionalTypes(op1, LanguageTypes.NUMBER, LanguageTypes.STRING)
                self.assertTypeEquality(op1, op2)

                output = MasterData(tipe=op1.tipe, value = op1.value + op2.value)

                self.pushStack(output)

            elif (current_op_code == OpCode.OP_SUB):
                op1 = self.popStack()
                op2 = self.popStack()

                self.assertType(op1, LanguageTypes.NUMBER)
                self.assertTypeEquality(op1, op2)

                output = MasterData(tipe=op1.tipe, value = op1.value - op2.value)

                self.pushStack(output)

            elif (current_op_code == OpCode.OP_MUL):
                op1 = self.popStack()
                op2 = self.popStack()

                self.assertType(op1, LanguageTypes.NUMBER)
                self.assertTypeEquality(op1, op2)

                output = MasterData(tipe=op1.tipe, value = op1.value * op2.value)

                self.pushStack(output)

            elif (current_op_code == OpCode.OP_DIV):
                op1 = self.popStack() 
                op2 = self.popStack()

                self.assertType(op1, LanguageTypes.NUMBER)
                self.assertTypeEquality(op1, op2)

                output = MasterData(tipe=op1.tipe, value = op1.value / op2.value)

                self.pushStack(output)

            ##################################################################################################
            elif (current_op_code == OpCode.OP_EQUAL):
                op1 = self.popStack() 
                op2 = self.popStack()

                self.assertTypeEquality(op1, op2)

                output = MasterData(tipe=LanguageTypes.BOOLEAN, value = op1.value == op2.value)

                self.pushStack(output)

            elif (current_op_code == OpCode.OP_LESS):
                op1 = self.popStack() 
                op2 = self.popStack()

                self.assertType(op1, LanguageTypes.NUMBER)
                self.assertTypeEquality(op1, op2)

                output = MasterData(tipe=LanguageTypes.BOOLEAN, value = op1.value < op2.value)
                self.pushStack(output)

            elif (current_op_code == OpCode.OP_LESS_EQUAL):
                op1 = self.popStack() 
                op2 = self.popStack()

                self.assertType(op1, LanguageTypes.NUMBER)
                self.assertTypeEquality(op1, op2)
               
                output = MasterData(tipe=LanguageTypes.BOOLEAN, value = op1.value <= op2.value)
                self.pushStack(output)

            elif (current_op_code == OpCode.OP_GREATER):
                op1 = self.popStack() 
                op2 = self.popStack()

                self.assertType(op1, LanguageTypes.NUMBER)
                self.assertTypeEquality(op1, op2)
                
                output = MasterData(tipe=LanguageTypes.BOOLEAN, value = op1.value > op2.value)
                self.pushStack(output)

            elif (current_op_code == OpCode.OP_GREATER_EQUAL):
                op1 = self.popStack() 
                op2 = self.popStack()

                self.assertType(op1, LanguageTypes.NUMBER)
                self.assertTypeEquality(op1, op2)
                
                output = MasterData(tipe=LanguageTypes.BOOLEAN, value = op1.value >= op2.value)
                self.pushStack(output)

            ##################################################################################################
            elif (current_op_code == OpCode.OP_AND):
                op1 = self.popStack() 
                op2 = self.popStack()

                self.assertType(op1, LanguageTypes.BOOLEAN)
                self.assertTypeEquality(op1, op2)

                output = MasterData(tipe=op1.tipe, value = op1.value and op2.value)

                self.pushStack(output)

            elif (current_op_code == OpCode.OP_OR):
                op1 = self.popStack() 
                op2 = self.popStack()

                self.assertType(op1, LanguageTypes.BOOLEAN)
                self.assertTypeEquality(op1, op2)

                output = MasterData(tipe=op1.tipe, value = op1.value or op2.value)

                self.pushStack(output)

            ##################################################################################################
            elif (current_op_code == OpCode.OP_NEG):
                op1 = self.popStack()

                self.assertType(op1, LanguageTypes.NUMBER)
                output = MasterData(tipe=op1.tipe, value = -op1.value)

                self.pushStack(output)

            elif (current_op_code == OpCode.OP_NOT):
                op1 = self.popStack()

                self.assertType(op1, LanguageTypes.BOOLEAN)
                output = MasterData(tipe=op1.tipe, value = not op1.value)

                self.pushStack(output)
            ##################################################################################################

            elif (current_op_code == OpCode.OP_PRINT):
                #the last value of the stack is popped because the very essence of statement is that 
                # it leaves the stack unmodified. when `print expr` is evaluated the `expr` modifies the 
                # the stack by adding a single result in the stack after the `popstack` the stack remain unchanged
                op = self.popStack()
                print(op.value)



            elif (current_op_code == OpCode.OP_POP):
                self.popStack()

            elif (current_op_code == OpCode.OP_PUSH):
                byte = self.getByte()
                data = MasterData(tipe=LanguageTypes.NUMBER, value=byte)
                self.pushStack(value=data)



            elif (current_op_code == OpCode.OP_PRINT):
                #the last value of the stack is popped because the very essence of statement is that 
                # it leaves the stack unmodified. when `print expr` is evaluated the `expr` modifies the 
                # the stack by adding a single result in the stack after the `popstack` the stack remain unchanged
                op = self.popStack()
                # print(op.value)

            elif (current_op_code == OpCode.OP_DEFINE_GLOBAL):
                variable_name = self.loadConstant()
                # when variable = expr is defined, expr pushes one value in the stack, 
                # assignment statement pops the value from the stack making the whole 
                # process producing no changes in the stack
                return_value = self.popStack()
                self.setIntoTable(key=variable_name.value, value=return_value, check_if_exists=False)
                # self.table[variable_name.value] = return_value

                # print('op_code define ', self.table)

            elif (current_op_code == OpCode.OP_LOAD_GLOBAL):
                variable_name = self.loadConstant()
                ret_value = self.getFromTable(key=variable_name.value)
                self.pushStack(ret_value) #the net effect is that op_load_global pushes one value in the stack

            elif (current_op_code == OpCode.OP_REDEFINE_GLOBAL):
                variable_name = self.loadConstant()
                # when variable = expr is defined, expr pushes one value in the stack, 
                # assignment statement pops the value from the stack making the whole 
                # process producing no changes in the stack
                return_value = self.popStack()

                self.setIntoTable(key=variable_name.value, value=return_value)

                # print('op_code define ', self.table)
            elif (current_op_code == OpCode.OP_LOAD_LOCAL):
                stack_entry_index = self.getByte() + self.getEBP()
                # when variable = expr is defined, expr pushes one value in the stack, 
                # assignment statement pops the value from the stack making the whole 
                # process producing no changes in the stack
                value = self.peekStack(stack_entry_index)

                self.pushStack(value)

            elif (current_op_code == OpCode.OP_SET_LOCAL):
                stack_entry_index = self.getByte() + self.getEBP()
                self.stack[stack_entry_index] = self.popStack()

            elif (current_op_code == OpCode.OP_JMP_IF_FALSE):
                offset = self.getByte() # get the else condition instruction pointer
                condition = self.popStack() # pop the condition from stack, the net result of the statement is nullified
                #condition must be of type BOOLEAN
                self.assertType(condition, LanguageTypes.BOOLEAN)
                # the following comparison can be done by directly comparing language constant, but for now we are using python native
                if condition.value == False:
                    self.offsetIP(offset)

            elif (current_op_code == OpCode.OP_JMP):
                offset = self.getByte() # get the else condition instruction pointer
                self.offsetIP(offset)

            elif (current_op_code == OpCode.OP_CALL):
                #### modify stack to include ebp ############
                EBP = MasterData(tipe=LanguageTypes.NUMBER, value=self.getEBP())
                self.pushStack(EBP)
                self.setEBP(self.getESP()) # set new value to ebp
                
                #############################################

                function_ip_index = self.getByte() # this returns the index of the function pointer that the ip should point to
                
                # actual_ip = self.table[function_ip_index]

                self.setIP(ip=function_ip_index)

            elif (current_op_code == OpCode.OP_RET):
                
                stack_index = self.getByte()
                return_pointer = self.peekStack(index=stack_index)
                print(' return pointer value : ', return_pointer.value)

                self.setIP(return_pointer.value) #jump to the caller environment 

                #on ret we pop all the value of the stack until ebp is equal to esp
                while self.getEBP() != self.getESP():
                    print(self.getEBP(), '-----esp ', self.getESP())
                    self.popStack()

                EBP = self.popStack()

                self.setEBP(ebp=EBP.value) # restore previous value to ebp

            else:
                self.reportVMError(f"unknown op_code at ip: {self.ip}, current_op_code: {current_op_code}")
        
        # print('computed ', [str(v) for v in self.stack])

    def setEBP(self, ebp):
        self.ebp = ebp

    def getEBP(self):
        return self.ebp 

    def advanceESP(self):
        self.esp += 1
    def reverseESP(self):
        self.esp -= 1

    def getESP(self):
        return self.esp

    def getOpCode(self):
        if (not self.isAtEnd()):
            ret_value = self.chunk.codeAt(self.ip)
            self.advance()
            return ret_value
        return None

    def setIP(self, ip):
        self.ip = ip

    def offsetIP(self, offset):
        self.ip += offset


    def isAtEnd(self):
        return len(self.chunk.codes) <= self.ip

    def advance(self):
        self.ip += 1

    def getByte(self):
        return self.getOpCode()

    def loadConstant(self):
        index = self.getByte()
        return self.chunk.constantAt(index)

    def popStack(self):
        print(self.ip, ' popping ', f"{[str(s) for s in self.stack[:-1]]}")
        self.reverseESP()
        return self.stack.pop()

    def pushStack(self, value):
        self.advanceESP()
        self.stack.append(value)
        print(self.ip, ' pushing ', f"{[str(s) for s in self.stack]}")

    def peekStack(self, index):
        return self.stack[index]

    def getCurrentInstructionLine(self):
        return self.chunk.lineAt(self.ip-1) #ip is already advance before the instruction is run 

    def getFromTable(self, key):
        try:
            return self.table[key]
        except KeyError as e:
                    self.reportError(f"variable `{variable_name.value}` is not defined")
        

    def setIntoTable(self, key, value, check_if_exists=True):
        if check_if_exists:
            self.table[key]

        self.table[key] = value
