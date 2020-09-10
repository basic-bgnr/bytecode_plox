from opcodes import OpCode
from values import MasterData, LanguageTypes, FunctionObject, NativeFunctionObject
import LanguageConstants

from enum import Enum

###for native functionality only 
import time
import random 
#Note: The vm's ip counter always points at the next instruction to execute
class Vm:
    def __init__(self, chunk=None):
        self.initializeChunk(chunk=chunk)
        self.initializeVm()

    def initializeVm(self):
        #self.table = {} #the reason this is only initialized once is due to the fact that initialization code pupulates it which is further utilized byt the program.

        INT_FUNCTION_IDENTIFIER = NativeFunctions.INT.value[0]
        INT_FUNCTION = NativeFunctionObject(name=INT_FUNCTION_IDENTIFIER, arity=1)
        INT_FUNCTION.setFunction(lambda x: MasterData(tipe=LanguageTypes.NUMBER, value=int(x.value)))

        STR_FUNCTION_IDENTIFIER = NativeFunctions.STR.value[0]
        STR_FUNCTION = NativeFunctionObject(name=STR_FUNCTION_IDENTIFIER, arity=1)
        STR_FUNCTION.setFunction(lambda x: MasterData(tipe=LanguageTypes.STRING, value=str(x.value)))

        TIME_FUNCTION_IDENTIFIER = NativeFunctions.TIME.value[0]
        TIME_FUNCTION = NativeFunctionObject(name=TIME_FUNCTION_IDENTIFIER, arity=0)
        TIME_FUNCTION.setFunction(lambda: MasterData(tipe=LanguageTypes.NUMBER, value=time.time_ns()))

        RANDOM_FUNCTION_IDENTIFIER = NativeFunctions.RANDOM.value[0]
        RANDOM_FUNCTION = NativeFunctionObject(name=RANDOM_FUNCTION_IDENTIFIER, arity=0)
        RANDOM_FUNCTION.setFunction(lambda: MasterData(tipe=LanguageTypes.NUMBER, value=random.random()))

        TYPE_FUNCTION_IDENTIFIER = NativeFunctions.TYPE.value[0]
        TYPE_FUNCTION = NativeFunctionObject(name=TYPE_FUNCTION_IDENTIFIER, arity=1)
        TYPE_FUNCTION.setFunction(lambda x: MasterData(tipe=LanguageTypes.STRING, value= f"<{x.tipe.name}>"))


        self.table = { INT_FUNCTION_IDENTIFIER:    MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=INT_FUNCTION),
                       STR_FUNCTION_IDENTIFIER:    MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=STR_FUNCTION),
                       TIME_FUNCTION_IDENTIFIER:   MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=TIME_FUNCTION),
                       RANDOM_FUNCTION_IDENTIFIER: MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=RANDOM_FUNCTION),
                       TYPE_FUNCTION_IDENTIFIER:   MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=TYPE_FUNCTION), }

    def initializeChunk(self, chunk=None):
        self.chunk = chunk
        self.stack = [] # constainer for MasterData
        self.ip = 0

        self.esp = 0 # extended stack pointer
        self.ebp = 0 # extended base pointer

        self.ebx = LanguageConstants.NIL # return value

        if self.chunk is not None:
            self.code_length = len(self.chunk.codes)
        else:
            self.code_length = 0



    def reportVMError(self, message):
        raise Exception(f"VM ERROR\n{message}\nAt line: {self.getCurrentInstructionLine()}")

    def reportError(self, message):
        raise Exception(f"{message}\nAt line: {self.getCurrentInstructionLine()}")

    def assertTypeEquality(self, op1, op2):
        if (op1.tipe == op2.tipe):
            return
        # op1.tipe.name, here .name can be called on `Enum` types to print their actual name
        self.reportError(f"type mismatch between the following:\n1. {op1}\n2. {op2}\nExpecting type: {op1.tipe.name}\nFound type: {op2.tipe.name}")

    def assertType(self, op1, tipe):
        if (op1.tipe == tipe):
            return
        self.reportError(f"operation can't be performed on: \n{op1}\nExpecting type: {tipe.name}\nFound type: {op1.tipe.name}")

    def assertOptionalTypes(self, op1, *tipes):
        if (op1.tipe in tipes):
            return
        self.reportError(f"operation can't be performed on:{op1.tipe.name}\nExpecting one of [{','.join([tipe.name for tipe in tipes])}] types")

    def assertArgumentEquality(self, function, number):
        if (function.value.arity == number.value):
            return 
        self.reportError(f"Argument mismatch for function {function}\nExpecting: {function.value.arity} args\nGot: {number.value} args")

    def exec(self, current_op_code):
        # breakpoint()
        if (current_op_code == OpCode.OP_LOAD_CONSTANT):
            constant_to_load =self.loadConstant()
            self.pushStack(constant_to_load)

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
            print(f"{op}")
            # breakpoint()



        elif (current_op_code == OpCode.OP_POP):
            self.popStack()

        elif (current_op_code == OpCode.OP_PUSH):
            byte = self.advanceByte()
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

            self.setIntoTable(key=variable_name.value, value=return_value, check_if_exists=True)

            # print('op_code define ', self.table)
        elif (current_op_code == OpCode.OP_LOAD_LOCAL):
            # breakpoint()
            stack_entry_index = self.getCurrentStackEntryIndex()


            # when variable = expr is defined, expr pushes one value in the stack, 
            # assignment statement pops the value from the stack making the whole 
            # process producing no changes in the stack
            value = self.peekStack(stack_entry_index)

            self.pushStack(value)

        elif (current_op_code == OpCode.OP_SET_LOCAL):
            stack_entry_index = self.getCurrentStackEntryIndex()
            value_to_put = self.popStack()

            self.putAtStack(index=stack_entry_index, value=value_to_put)

        elif (current_op_code == OpCode.OP_JMP_IF_FALSE):
            offset = self.advanceByte() # get the else condition instruction pointer
            condition = self.popStack() # pop the condition from stack, the net result of the statement is nullified
            #condition must be of type BOOLEAN
            self.assertType(condition, LanguageTypes.BOOLEAN)
            # the following comparison can be done by directly comparing language constant, but for now we are using python native
            if condition.value == False:
                self.offsetIP(offset)

        elif (current_op_code == OpCode.OP_JMP):
            offset = self.advanceByte() # get the else condition instruction pointer
            self.offsetIP(offset)

        elif(current_op_code == OpCode.OP_GOTO):
            goto_location  = self.advanceByte()
            self.setIP(ip=goto_location)

        elif (current_op_code == OpCode.OP_CALL):
            #### modify stack to include ebp ############
            # breakpoint()
            function_object = self.popStack()
            num_args        = self.popStack()

            self.assertOptionalTypes(function_object, LanguageTypes.FUNCTION, LanguageTypes.NATIVE_FUNCTION)
            self.assertArgumentEquality(function_object, num_args)


            EBP = MasterData(tipe=LanguageTypes.NUMBER, value=self.getEBP())
            self.pushStack(EBP)
            self.setEBP(self.getESP()) # set new value to ebp
            
            #############################################
            #in case of native function, new ip is not set however all equivalent procedures are carried out to simulate function call
            #the following if branch simulates function call, and return
            if function_object.tipe == LanguageTypes.NATIVE_FUNCTION:
                # breakpoint()
                
                custom_function = function_object.value
                #int(num_args_value) is required because its floating point by default
                args = [self.peekStack(i + self.getEBP()) for i in reversed(range(-3 - int(num_args.value) + 1, -3+1))]

                try:                
                    return_value = custom_function.call(*args) #
                except Exception as e:
                    self.reportError(message=f"{e.args[0]}")

                self.pushStack(return_value) # this is just a formality, function value must be put on the stack, its cleaned during stackcleanup. But before that we set the ebx register
                self.setEBX(return_value)

                self.stackCleanup()
                

            else:
                function_ip_index = function_object.value.ip # this returns the index of the function pointer that the ip should point to
                
                # actual_ip = self.table[function_ip_index]

                self.setIP(ip=function_ip_index)

        elif (current_op_code == OpCode.OP_SET_EBX):
            return_value = self.popStack()
            # self.pushStack(value=return_value)

            self.setEBX(return_value)

        elif (current_op_code == OpCode.OP_LOAD_EBX):
            stack_value = self.getEBX()
            self.pushStack(value=stack_value)
            #once read reset it back to NIL
            self.setEBX(LanguageConstants.NIL)

        elif (current_op_code == OpCode.OP_RET):
            # breakpoint()

            relative_index = -2 # ret ptr is -2 offset from the ebp
            stack_index = relative_index + self.getEBP()
            return_pointer = self.peekStack(index=stack_index)
            # print(' return pointer value : ', return_pointer.value)

            #here we need to int the returned value since it's being converted from internal NUMBER type which is floating point
            self.setIP(int(return_pointer.value)) #seth the callee environment
            self.stackCleanup() #cleanup temporaries value in created in the function frame

        else:
            self.reportVMError(f"unknown op_code at ip: {self.getIP()}, current_op_code: {current_op_code}")
        
        # print('computed ', [str(v) for v in self.stack])

    def run(self, chunk=None, initializing_codes=None, start_at=0):

        if initializing_codes is not None:
            # initialize the program
            self.initializeChunk(chunk=initializing_codes)
            self.run_() 

        if chunk is None:
            self.reportError(message="main bytearray is not included")
        

        
        self.initializeChunk(chunk=chunk)
        self.setIP(start_at)
        self.run_()

    def stackCleanup(self):
     #on ret we pop all the value of the stack until ebp is equal to esp
        while self.getEBP() != self.getESP():
            # print(self.getEBP(), '-----esp ', self.getESP())
            self.popStack()

        EBP = self.popStack()

        self.setEBP(ebp=EBP.value) # restore previous value to ebp

        # self.pushStack(self.getEBX()) # push the ebx value in the stack stack, it is done because the function must change the stack as it's evaluated as expression

        # self.setEBX(LanguageConstants.NIL)

    def run_(self):
        while current_op_code := self.advanceOpCode():
            self.exec(current_op_code)


    # calculate the location of stack variable when function frame is entered
    def getCurrentStackEntryIndex(self):
        # breakpoint()
        #abs is done so that, -ve value is not produced when entering block statement, when epb is 0
        # print('ip ', self.ip)
        # print('stack entry value in byte ', self.advanceByte(), '  ', self.getEBP(), ' -> ',type(self.advanceByte()), type(self.getEBP()),", ", ' ip-> ', self.ip)
        # ebp = self.getEBP()
        # relative_stack_index = self.advanceByte()
        # print('stack entry value in byte ', relative_stack_index, '  ', ebp, ' -> ',type(relative_stack_index), type(ebp),", ", ' ip-> ', self.ip)
        # if relative_stack_index > 0: # temp varaible in block are calculated in 

        #     return relative_stack_index

        # absolute_stack_index = ebp + relative_stack_index -1 #function args are negative
        # print('stack entry index ',absolute_stack_index)
        # return absolute_stack_index

        return self.getEBP() + self.advanceByte()

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

    def advanceOpCode(self):
        # breakpoint()
        if (not self.isAtEnd()):
            ret_value = self.chunk.codeAt(self.getIP())
            self.advance()
            # breakpoint()
            return ret_value
        # breakpoint()
        return None

    def setIP(self, ip):
        self.ip = ip

    def offsetIP(self, offset):
        self.ip += offset

    def getIP(self):
        return self.ip

    def isAtEnd(self):
        return self.getIP() >= self.code_length

    def advance(self):
        self.setIP(ip=self.getIP() + 1)

    def advanceByte(self):

        return_byte = self.advanceOpCode()
        return return_byte

    def loadConstant(self):
        index = self.advanceByte()
        # breakpoint()
        return self.chunk.constantAt(index)

    def popStack(self):
        # print(self.ip, ' popping ', f"{[str(s) for s in self.stack[:-1]]}")
        # print('ebx ', self.getEBX())
        self.reverseESP()
        return self.stack.pop()

    def pushStack(self, value):
        self.advanceESP()
        self.stack.append(value)
        # print(self.ip, ' pushing ', f"{[str(s) for s in self.stack]}")
        # print('ebx ', self.getEBX())

    def peekStack(self, index):
        # breakpoint()
        # if index < 0: #relative indexing for function 
        return self.stack[index]
        # return self.stack[index]
    def putAtStack(self, index, value):
        self.stack[index] = value

   
    def getCurrentInstructionLine(self):
        return self.chunk.lineAt(self.getIP()-1) #ip is already advance before the instruction is run 

    def getFromTable(self, key):
        # breakpoint()
        try:
            return self.table[key]
        except KeyError as e:
            self.reportError(f"variable `{key}` is not defined")
    

    def setIntoTable(self, key, value, check_if_exists=True):
        if check_if_exists:
            self.getFromTable(key)

        self.table[key] = value

    def setEBX(self, ebx):
        self.ebx = ebx

    def getEBX(self):
        return self.ebx

class NativeFunctions(Enum):
    INT    = 'int',
    STR    = 'str',
    TIME   = 'time',
    RANDOM = 'random',
    TYPE   = 'type',