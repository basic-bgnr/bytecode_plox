from ByteArray import Chunk
from opcodes import OpCode
from lexer import TokenType
from values import LanguageTypes, MasterData, FunctionObject, ClassObj, InstanceObj
import LanguageConstants

from itertools import count

from ASTPrinter import ASTPrinter
from parser import LiteralExpression, GetExpression


#helper class to manage local variable in program stack
class ScopeEntity:
    def __init__(self, name, scope_depth, index = None):
        self.name = name #name is for resolving, finding variable by equating
        self.scope_depth = scope_depth# scope depth is for popping the value when scope is ended

        self.index = index #

    def __str__(self):
        return f"<ScopeEntity : name: {self.name:}, scope_depth: {self.scope_depth}, scope_index: {self.index}>"

class LoopModifierEntity:
    def __init__(self, parent_loop_scope_depth, instruction_pointer_location):
        self.parent_loop_scope_depth = parent_loop_scope_depth
        self.instruction_pointer_location = instruction_pointer_location

    def __str__(self):
        return f"parent_scope_depth: {self.parent_loop_scope_depth}   instruction_pointer_location: {self.instruction_pointer_location}"
        

class Compiler:
    def __init__(self):
        self.chunk = Chunk()

        self.scope_depth = 0
        self.scope_entities = []# position of ScopeEntity is the position of the variable in the stack, enumerate(scapepositoin) => (stack_index, scope_entitiy)
        self.variable_in_scope = 0 #this is for calculating the number of times we need to pop, to remove the local variable from stack

        self.function_table = {}
        
        self.scope_enitity_relative_point = 0

        self.initializing_codes = Chunk() #runtime setup codes

        self.initializing_codes.linkConstantPoolWithParent(parent=self.chunk)

        self.break_modifier_entities = []
        self.continue_modifier_entities = []

        self.is_inside_class = False 
    ###########################################################################
    def setInsideClass(self, value):
        self.is_inside_class = value

    def isInsideClass(self):
        return self.is_inside_class

    def peekBreakEntityAt(self):
        for entity in reversed(self.break_modifier_entities):
            if entity.parent_loop_scope_depth == scope_depth:
                return entity


    def peekContinueEntityAt(self, scope_depth):
        for entity in reversed(self.continue_modifier_entities):
            if entity.parent_loop_scope_depth == scope_depth:
                return entity


    def peekContinueEntity(self):
        return self.continue_modifier_entities[-1]

    def peekBreakEntity(self):
        return self.break_modifier_entities[-1]

    def popBreakEntity(self):
        return self.break_modifier_entities.pop()

    def popContinueEntity(self):
        return self.continue_modifier_entities.pop()

    def pushBreakEntity(self, break_entity):
        self.break_modifier_entities.append(break_entity)

    def pushContinueEntity(self, continue_entity):
        self.continue_modifier_entities.append(continue_entity)

    ###########################################################################
    def reportCompilerError(self, message):
        raise Exception(f"COMPILER ERROR\n{message}")

    def reportError(self, message):
        raise Exception(f"{message}")


    def addInitializingCode(self, code, line_num):
        #todo: convert the initializing_code vairable into bytearray class
        self.initializing_codes.pushOpCode(op_code=code, at_line=line_num)

    def makeScopeEntititiesRelativeTo(self, datum):
        self.scope_enitity_relative_point = datum

    def getScopeEntittiesDatum(self):
        return self.scope_enitity_relative_point

    def popScopeEntity(self):
        return self.scope_entities.pop()
    def pushScopeEntity(self, scope_entity):
        self.scope_entities.append(scope_entity)

    def setScopeDepth(self, scope_depth):
        self.scope_depth = scope_depth

    def getscopeDepth(self):
        return self.scope_depth

    def advanceScopeDepth(self):
        # breakpoint()
        return self.setScopeDepth(self.getscopeDepth() + 1)

    def reverseScopeDepth(self):
        return self.setScopeDepth(self.getscopeDepth() - 1)

    def getScopeEntitiesSize(self):
        return len(self.scope_entities)

    def isScopeEntitiesEmpty(self):
        return self.getScopeEntitiesSize() == 0

    def getLastScopeEntityDepth(self):
        return self.scope_entities[-1].scope_depth

    ###############################################################################to remove
    def addToFunctionTable(self, function):
        if self.scope_depth == 0:
            self.function_table[function.caller_expr.expr.literal] = (self.getNextIPLocation(), function.caller_expr.expr.line)

    def getFunctionPointer(self, function_name):
        try:
            return self.function_table[function_name][0] #(x, y) 
        except KeyError:
            self.reportError(f"{function_name} function is not called")
    ###############################################################################
    def getNextIPLocation(self):#this is to modify the next byteelf):
        return self.chunk.getNextIPLocation() #this is to modify the next byte

    def compileAll(self, AST):
        for AS in AST:
            self.compile(AS)
            # if self.compile(AS) is None:
            #   raise Expception("none occured ", AS)

        # try:
        #   return self.getFunctionPointer(function_name='main')
        # except:
        #   raise Exception("program must have function named 'main' as the only entry point")
        # breakpoint()
        if len(self.function_table) > 1:
            print(self.function_table)
            lines = ', '.join([str(line_num) for key, (_, line_num) in self.function_table.items() if key != 'main'])
            self.reportError(message = f"More than one global function call at line: {lines}")

        return self.getFunctionPointer(function_name='main')


    def compile(self, AS):
        if AS is not None:
            return AS.linkVisitor(self)

    def makeConstant(self, constant):
        return self.chunk.makeConstant(constant)

    def emitCode(self, op_code, at_line):
        # print('emit code ', op_code)
        self.chunk.pushOpCode(op_code, at_line)

    def emitByte(self, byte, at_line):
        self.emitCode(byte, at_line)

    def modifyByteAt(self, byte, index):
        self.chunk.pushOpCodeAt(byte, index)

    def emitCodes(self, op_code1, op_code2, at_line):
        self.chunk.pushOpCodes(op_code1, op_code2, at_line)



    def pushConstant(self, constant, at_line):
        return self.chunk.pushConstant(constant, at_line)

    def visitLiteralExpression(self, literal_expression):

        if (literal_expression.expr.tipe is TokenType.NUMBER):
            
            number = MasterData(tipe= LanguageTypes.NUMBER, value = literal_expression.value)
            self.pushConstant(number, at_line = literal_expression.expr.line)

        elif (literal_expression.expr.tipe is TokenType.TRUE):          
            self.pushConstant(LanguageConstants.TRUE, at_line = literal_expression.expr.line)

        elif (literal_expression.expr.tipe is TokenType.FALSE):
            self.pushConstant(LanguageConstants.FALSE, at_line = literal_expression.expr.line)

        elif (literal_expression.expr.tipe is TokenType.NIL):
            self.pushConstant(LanguageConstants.NIL, at_line = literal_expression.expr.line)

        elif (literal_expression.expr.tipe is TokenType.STRING):

            string = MasterData(tipe= LanguageTypes.STRING, value = literal_expression.value)
            self.pushConstant(string, at_line = literal_expression.expr.line)

        ##todo: identifier_token implementation 
        elif (literal_expression.expr.tipe in [TokenType.IDENTIFIER, TokenType.THIS]):
            
            local_variable_index = self.resolveLocalVariable(literal_expression.expr.literal)
            if (local_variable_index is not None):
                self.emitCodes(OpCode.OP_LOAD_LOCAL, local_variable_index, at_line=literal_expression.expr.line)
            else:
                variable_name = MasterData(tipe=LanguageTypes.STRING, value=literal_expression.expr.literal)

                # self.chunk.pushConstant(string, at_line = literal_expression.expr.line)

                # lvalue_name = MasterData(tipe=LanguageTypes.STRING, value=assignment_statement.lvalue.expr.literal)

                global_variable_index = self.makeConstant(variable_name)
                
                # self.chunk.push(OpCode.OP_LOAD_GLOBAL, at_line=line_num)
                # self.chunk.push(global_variable_index, at_line=line_num)

                self.emitCodes(OpCode.OP_LOAD_GLOBAL, global_variable_index, at_line=literal_expression.expr.line)

        else: 
            raise Exception("no code for value other than number")

        return literal_expression.expr.line

    def visitUnaryExpression(self, unary_expression):
        literal_expression = unary_expression.right
        operator = unary_expression.operator

        line_num = self.compile(literal_expression)

        if (operator.tipe == TokenType.MINUS):
            self.emitCode(OpCode.OP_NEG, at_line=operator.line)
        elif(operator.tipe == TokenType.BANG):
            self.emitCode(OpCode.OP_NOT, at_line=operator.line)

        return line_num


    def visitBinaryExpression(self, binary_expression):
        right = binary_expression.right
        left  = binary_expression.left
        operator = binary_expression.operator

        # here the order in which the following two expr is compiled to important when 
        # popping the value for calculation in the virtual machine
        self.compile(right)
        line_num = self.compile(left)
        

        if (operator.tipe == TokenType.PLUS):
            self.emitCode(OpCode.OP_ADD, at_line = operator.line)

        elif (operator.tipe == TokenType.MINUS):
            self.emitCode(OpCode.OP_SUB, at_line = operator.line)

        elif (operator.tipe == TokenType.STAR):
            self.emitCode(OpCode.OP_MUL, at_line = operator.line)

        elif (operator.tipe == TokenType.SLASH):
            self.emitCode(OpCode.OP_DIV, at_line = operator.line)

        elif (operator.tipe == TokenType.AND):
            self.emitCode(OpCode.OP_AND, at_line = operator.line)

        elif (operator.tipe == TokenType.OR):
            self.emitCode(OpCode.OP_OR, at_line = operator.line)

        elif (operator.tipe == TokenType.EQUAL_EQUAL):
            self.emitCode(OpCode.OP_EQUAL, at_line = operator.line)
        ################################################### 
        elif (operator.tipe == TokenType.BANG_EQUAL):
            self.emitCode(OpCode.OP_EQUAL, at_line = operator.line)
            self.emitCode(OpCode.OP_NOT, at_line = operator.line)

        ################################################### 
        elif (operator.tipe == TokenType.LESS):
            self.emitCode(OpCode.OP_LESS, at_line = operator.line)

        elif (operator.tipe == TokenType.LESS_EQUAL):
            self.emitCode(OpCode.OP_LESS_EQUAL, at_line = operator.line)

        elif (operator.tipe == TokenType.GREATER):
            self.emitCode(OpCode.OP_GREATER, at_line = operator.line)

        elif (operator.tipe == TokenType.GREATER_EQUAL):
            self.emitCode(OpCode.OP_GREATER_EQUAL, at_line = operator.line)

        return line_num



    def GroupingExpression(self, grouping_expression):
        return self.compile(grouping_expression.expression)

    def visitExpressionStatement(self, expression_statement):
        #to do check case for null statement
        #the following conditional is for global_variable
        
        if expression_statement.expr:
            #to do: use line_num
            line_num = self.compile(expression_statement.expr)
            self.emitCode(OpCode.OP_POP, at_line=line_num) # extra pop due to function expression statement is due to this.
            return line_num

    def visitPrintStatement(self, print_statement):
        # the follwing conditition check allows print statement without any expression as having no effect
        if print_statement.expr:
            line_num = self.compile(print_statement.expr)
            self.emitCode(OpCode.OP_PRINT, at_line=line_num)
            return line_num

    def visitBlockStatement(self, block_statement):
        # breakpoint()
        self.beginScope()
        line_num = 0
        for statement in block_statement.statements:
            line_num = self.compile(statement)

        self.endScope(line_num)

        
        return line_num


    def beginScope(self):
        self.advanceScopeDepth();
        
    def endScope(self, line_num, is_function_statement=False):
        self.reverseScopeDepth()
        # this is for calculating the number of times we need to pop, to remove the local variable from stack
        while not self.isScopeEntitiesEmpty() and self.getLastScopeEntityDepth() > self.getscopeDepth():
            if not is_function_statement:# function caller is responsible for popping
                self.emitCode(OpCode.OP_POP, at_line=line_num)
            self.popScopeEntity()

            

    def visitAssignmentStatement(self, assignment_statement):
      
        if (isinstance(assignment_statement.lvalue, GetExpression)):
            #compile the rhs
            line_num = self.compile(assignment_statement.rvalue)
            
            #compile the lhs 
            line_num = self.pushConstant(constant=MasterData(tipe=LanguageTypes.STRING, value=assignment_statement.lvalue.prop_or_method.literal), at_line=line_num)
            line_num = self.compile(assignment_statement.lvalue.expr)

            self.emitCode(op_code=OpCode.OP_SET_PROPERTY, at_line=line_num)

            return line_num


          #if assignment takes place inside block the following compile function, put the rvalue in the stack
        # but the global variable table remains unchanged, local variables are managed completely by using the
        # stack

        #carry out the follwing only when the variables are decalared in local context

        if (self.isLocal()):
            #compute local variable reference, most recent local variable is already in the stack as 
            #a result of `self.compile(assignmen_statement.rvalue) [see above]
            # self.addLocalAssignment(assignment_statement)
            return self.addLocalAssignment(assignment_statement)
        else:
            return self.addGlobalAssignment(assignment_statement)

    def visitReassignmentStatement(self, reassignment_statement):

        if (isinstance(reassignment_statement.lvalue, GetExpression)):
            # compile rhs
            line_num = self.compile(reassignment_statement.rvalue)

            # compile lhs
            line_num = self.pushConstant(constant=MasterData(tipe=LanguageTypes.STRING, value=reassignment_statement.lvalue.prop_or_method.literal), at_line=line_num)
            line_num = self.compile(reassignment_statement.lvalue.expr)
            

            self.emitCode(op_code=OpCode.OP_SET_PROPERTY, at_line=line_num)

            return line_num

        #if assignment takes place inside block the following compile function, put the rvalue in the stack
        # but the global variable table remains unchanged, local variables are managed completely by using the
        # stack

        #carry out the follwing only when the variables are decalared in local context
        if (self.isLocal()):
            #compute local variable reference, most recent local variable is already in the stack as 
            #a result of `self.compile(assignmen_statement.rvalue) [see above]
            # self.addLocalReassignment(reassignment_statement)
            return self.addLocalReassignment(reassignment_statement)
        else:
            return self.addGlobalReassignment(reassignment_statement)
    
    def isLocal(self):
        return self.getscopeDepth()>0

    def addGlobalReassignment(self, reassignment_statement):
        line_num = self.compile(reassignment_statement.rvalue)
        lvalue_name = MasterData(tipe=LanguageTypes.STRING, value=reassignment_statement.lvalue.expr.literal)

        global_variable_index = self.makeConstant(lvalue_name)
        self.emitCodes(OpCode.OP_REDEFINE_GLOBAL, global_variable_index, at_line=line_num)
        return line_num

    def addGlobalAssignment(self, assignment_statement):
        line_num = self.compile(assignment_statement.rvalue) # this pushes rvalue in the program stack
        lvalue_name = MasterData(tipe=LanguageTypes.STRING, value=assignment_statement.lvalue.expr.literal)

        global_variable_index = self.makeConstant(lvalue_name)#make the lvalue into MasterData and store it in the constant table
        self.emitCodes(OpCode.OP_DEFINE_GLOBAL, global_variable_index, at_line=line_num)
        return line_num

    def addLocalAssignment(self, assignment_statement):
        
        #push the value in stack, this works because the upper code adds local variable which can be resolved 
        #during compiling literalexpression
        line_num = self.compile(assignment_statement.rvalue) # this just put the rvalue in the stack

        #################################################################
        lvalue_name = assignment_statement.lvalue.expr.literal #local variable name

        scope_entity = ScopeEntity(name=lvalue_name, scope_depth=self.getscopeDepth())
        self.addScopeEntity(scope_entity)
        #################################################################

        return line_num

    def addLocalReassignment(self, reassignment_statement):
        lvalue_name = reassignment_statement.lvalue.expr.literal #local variable name
        #in reassignement, the variable has already been put in the stack, so just resolve it
        local_stack_index = self.resolveLocalVariable(lvalue_name)
         # the variable is local
        if local_stack_index is not None: 
            line_num = self.compile(reassignment_statement.rvalue)
            # print('reassign ', local_stack_index)
            self.emitCodes(OpCode.OP_SET_LOCAL, local_stack_index, at_line=line_num)
        else:
            return self.addGlobalReassignment(reassignment_statement)

        return line_num

    def resolveLocalVariable(self, var_name):
        #the scope_entities needs to transversed in reverse order so as to simulate a stack
        # note: this function can return [int, None], when it returns 0, the variable is self referencing or, it may be a reassignment statement
        # when 0 is returned, it should be separately handled for assignment and reassignment case
        
        # reversed_scope_entities = reversed(self.scope_entities)
        # stack_indexes = reversed(range(len(reversed_scope_entities)))

        # for stack_index, scope_entity in reversed(list(enumerate(self.scope_entities))):
        #   if scope_entity.name == var_name:
        #       # print('ressolved ', var_name)
        #       return stack_index
        # return None
        for scope_entity in reversed(self.scope_entities):
            if scope_entity.name == var_name:
                # print('ressolved ', var_name)
                # breakpoint()
                return scope_entity.index
        return None

    def visitReturnStatement(self, return_statement):
        if return_statement.expr is not None:
            line_num = self.compile(return_statement.expr)
            self.emitCode(op_code=OpCode.OP_SET_EBX, at_line=line_num)

        else:
            line_num = 100; # empty return statement won't produce any error, so putting random value
        
        self.emitCode(op_code=OpCode.OP_RET, at_line=line_num)
        return line_num

    def visitContinueStatement(self, continue_statement):
        line_num = continue_statement.token.line
        
        
        goto_entity = self.peekContinueEntity()
        # breakpoint()
        #cleanup temporary stack
        for scope_entity in reversed(self.scope_entities):
            if goto_entity.parent_loop_scope_depth < scope_entity.scope_depth:
                self.emitCode(op_code=OpCode.OP_POP, at_line=line_num)
            else:
                break

        self.emitCode(op_code=OpCode.OP_GOTO, at_line=line_num)
        goto_ip_location = self.getNextIPLocation()
        self.emitByte(byte=goto_entity.instruction_pointer_location, at_line=line_num) #this byte will get modified later on 
        goto_entity.instruction_pointer_location = goto_ip_location
        
        # breakpoint()

        return line_num

    def visitBreakStatement(self, break_statement):
        line_num = break_statement.token.line
        # breakpoint()
    
        goto_entity = self.peekBreakEntity()
        #cleanup temporary stack
        for scope_entity in reversed(self.scope_entities):
            if goto_entity.parent_loop_scope_depth < scope_entity.scope_depth:
                self.emitCode(op_code=OpCode.OP_POP, at_line=line_num)
            else:
                break

        self.emitCode(op_code=OpCode.OP_GOTO, at_line=line_num)
        goto_ip_location = self.getNextIPLocation()
        self.emitByte(byte=goto_entity.instruction_pointer_location, at_line=line_num)
        goto_entity.instruction_pointer_location = goto_ip_location

        # breakpoint()
        
        return line_num



    def visitFunctionStatement(self, function_statement):
        # print('in function statemetn')
        
        ip = self.getNextIPLocation()
        ##############################################################################
        if not self.isInsideClass(): #only global function are callable by names

            function_name = function_statement.function_identifier_expression.expr.literal
            params_length = len(function_statement.params_list)

            function_constant = MasterData(tipe=LanguageTypes.FUNCTION, value=FunctionObject(name=function_name, arity=params_length, ip=ip))
            function_index = self.makeConstant(constant=function_constant)

            #this is for use in the vm for indexing function table 
            function_name_constant = MasterData(tipe=LanguageTypes.STRING, value=function_name)
            function_name_constant_index = self.makeConstant(constant=function_name_constant)

            ##insert these statement at the beginning of the program so that function can be called at runtime instead at compiletime
            self.addInitializingCode(OpCode.OP_LOAD_CONSTANT, line_num=0)
            self.addInitializingCode(function_index, line_num=0)

            self.addInitializingCode(OpCode.OP_DEFINE_GLOBAL, line_num=0)
            self.addInitializingCode(function_name_constant_index, line_num=0)

        ###################################################
        self.beginScope()

        # add the value in the stack in reverse order, this is done so because resolveVariable functoion reversee the varaible is order to  simulate stack
        ####two dummy value to simulate caller convention#######

        self.addScopeEntity(ScopeEntity(name="@ebp", scope_depth=self.getscopeDepth(), index = -1) , default=False)
        self.addScopeEntity(ScopeEntity(name="@retptr", scope_depth=self.getscopeDepth(), index = -2), default=False)


        #######################################################

        indices = count(start=-3, step=-1)

        for index, param in zip(indices, reversed(function_statement.params_list)):
            self.addScopeEntity(ScopeEntity(name=param.expr.literal, scope_depth=self.getscopeDepth(), index=index), default=False)

        middle_point = self.getScopeEntitiesSize()
        self.makeScopeEntititiesRelativeTo(datum=middle_point)
        

        line_num = self.compile(function_statement.block_statement)


        self.makeScopeEntititiesRelativeTo(datum=0)
        # print('---------------------------now here')

        self.emitCode(OpCode.OP_RET, at_line=line_num) #this is single OpCode
        # self.emitByte(self.resolveLocalVariable("@retptr"), at_line=line_num)

        self.endScope(line_num, is_function_statement=True)#the second arguemnt causes to not emit `pop` code


        #push the return value in the stack

        # breakpoint()
        # self.scope_entities.pop()#remove retptr and ebp
        # self.scope_entities.pop()

        return line_num

    def visitCallableExpression(self, function_expression):
        # print('incallable')
        self.addToFunctionTable(function=function_expression)
        
        line_num =0 #dummy value 
        for arg in function_expression.args:
            line_num = self.compile(arg) # push the args in the stack
        #return pointer address, make the pointer address constant and load it using OP_CONSTANT
        
        self.emitCode(OpCode.OP_LOAD_CONSTANT, at_line=line_num)
        index_to_modify_ret_ptr = self.getNextIPLocation() #this is to modify the next byte
        self.emitByte(byte=None, at_line=line_num) # we fill it with none, because now we don't know where the return pointer should point to

        
        self.pushConstant(MasterData(tipe=LanguageTypes.NUMBER, value=len(function_expression.args)), at_line=line_num) #pus the current no of argument supplied to the function, this used for checking if correct no. of arugment is supplied during runtime
        self.compile(function_expression.caller_expr) #load the function object in the stack

        self.emitCode(OpCode.OP_CALL, at_line=line_num)
        
        #byte can also be made cosntant, OP_CONSTANT

        # self.emitByte(byte=self.getFunctionPointer(function_name), at_line=line_num)


        ret_pointer_index = self.makeConstant(constant=MasterData(tipe=LanguageTypes.NUMBER, value=self.getNextIPLocation()))#this is to modify the next byte), at_line=line_num)
        # print('ret_pointer_index ', ret_pointer_index)
        self.modifyByteAt(byte=ret_pointer_index, index=index_to_modify_ret_ptr)# this set the value of the byte previously set o None, as we now know where the function is going to end


        # The following pop instruction is not required because the endscope() function does that already

        self.emitCode(OpCode.OP_POP, at_line=line_num) #pop the ret_ptr
        # # print("-------------")
        for arg in function_expression.args:#pop all argument 
            # print('arg')
            self.emitCode(OpCode.OP_POP, at_line=line_num)

        self.emitCode(op_code=OpCode.OP_LOAD_EBX, at_line=line_num)

        #push the return value in the stack



        # self.emitCode(OpCode.OP_LOAD_EBX, at_line=line_num)



        # print("============")
        # breakpoint()
        return line_num



    def addScopeEntity(self, scope_entity, default=True):
        if default:
            scope_entity.index = self.getScopeEntitiesSize() - self.getScopeEntittiesDatum() #this makes the referencing relative

        self.pushScopeEntity(scope_entity)

        # print([str(s) for s in self.scope_entities])

    def getInstructionPointerSize(self):
        return self.chunk.getCodesLength()

    def visitIfStatement(self, if_statement):

        line_num = self.compile(if_statement.expression) # this pushes the value in the stack
        
        
        self.emitCode(OpCode.OP_JMP_IF_FALSE, line_num)
        self.emitByte(None, line_num)# just some random byte, we'll fill it up with true value once the conditional statements are compiled

        branch_if_start_instruction_pointer = self.getInstructionPointerSize()-1 # this points to the above byte

         
        if_line_num = self.compile(if_statement.if_block_statement) #push the branch code in the code stack

        if (if_statement.else_block_statement is None):

            branch_if_end_instruction_pointer = self.getInstructionPointerSize()-1 #points to above byte
            offset_if = branch_if_end_instruction_pointer - branch_if_start_instruction_pointer # the number of additional line pushed in the codes stack

            self.modifyByteAt(byte=offset_if, index=branch_if_start_instruction_pointer)# update the None byte to offset

            return if_line_num

        else:

            self.emitCode(OpCode.OP_JMP, at_line=if_line_num)#we put this jump statement so that if the condition is true, the code executes as usual and jump unconditionally after reaching the end of true block, it needs to jump by amount of size of else block.
            self.emitByte(None, at_line=if_line_num) # just some random byte, we'll fill it up with true value one the 
            

            branch_if_end_instruction_pointer = self.getInstructionPointerSize()-1 #points to above byte

            offset_if = branch_if_end_instruction_pointer - branch_if_start_instruction_pointer # the number of additional line pushed in the codes stack

            self.modifyByteAt(byte=offset_if, index=branch_if_start_instruction_pointer)# update the None byte to offset

            
            else_line_num = self.compile(if_statement.else_block_statement)
        
            branch_else_end_instruction_pointer = self.getInstructionPointerSize()-1

            offset_else = branch_else_end_instruction_pointer - branch_if_end_instruction_pointer
            
            self.modifyByteAt(byte=offset_else, index=branch_if_end_instruction_pointer)# push offset to the end of true statement's end
            
            return else_line_num

    def visitWhileStatement(self, while_statement):

        self.pushBreakEntity(break_entity=LoopModifierEntity(parent_loop_scope_depth=self.getscopeDepth(), instruction_pointer_location=None))#we don't know the ip location now
        self.pushContinueEntity(continue_entity=LoopModifierEntity(parent_loop_scope_depth=self.getscopeDepth(), instruction_pointer_location=None))#we don't know the ip location now

        top_label_instruction_pointer = self.getInstructionPointerSize() # this points to below expression


        line_num = self.compile(while_statement.expression) # put the condition expression in the stack

        self.emitCodes(OpCode.OP_JMP_IF_FALSE, None, at_line=line_num) #put random byte at the jump location
        branch_if_start_instruction_pointer = self.getInstructionPointerSize() - 1 # this indexes the above Null byte 

        #compile loop code 

        loop_line_num = self.compile(while_statement.block_statement)
       
        ###########
        self.modifyContinueInstructionPointer() #starts continue from here, reason for while statement to have additonal end_block_statement
        ###########
        
        loop_line_num = self.compile(while_statement.end_block_statement)


        branch_if_end_instruction_pointer = self.getInstructionPointerSize() + 1 + 1 # this points to the following op_jmp, but we need to add one since loop ofset variable is also in the code stack and an additional 1 so that the ip_counter point next to it.

        loop_offset = top_label_instruction_pointer - branch_if_end_instruction_pointer  # this is negative, as we need to go upward
        self.emitCodes(OpCode.OP_JMP, loop_offset, at_line=loop_line_num) # this loops to the start o the top_level_counter
        
        false_condition_instruction_pointer = self.getInstructionPointerSize() - 1 #this points to the instruction after the above OP_JMP

        self.modifyBreakInstructionPointer()#starts break from here

        false_offset = false_condition_instruction_pointer - branch_if_start_instruction_pointer
        self.modifyByteAt(byte=false_offset, index=branch_if_start_instruction_pointer)

        # breakpoint()


        #pop it after we've compiled all the block statements
        self.popContinueEntity()
        self.popBreakEntity()


        return line_num


    def modifyContinueInstructionPointer(self):
        #check if continue statement is defined in the block_statment
        continue_entity = self.peekContinueEntity()
        if index := continue_entity.instruction_pointer_location:
            modified_ip = self.getInstructionPointerSize()
            self.modifyByteAt(byte=modified_ip, index=index)


    def modifyBreakInstructionPointer(self):
    #check if break statement is defined in the block_statment
        break_entity = self.peekBreakEntity()
        if index := break_entity.instruction_pointer_location:
            modified_ip = self.getInstructionPointerSize()
            self.modifyByteAt(byte=modified_ip, index=index)

    def visitGetExpression(self, get_expression):
        expr = get_expression.expr 
        prop_or_method_token = get_expression.prop_or_method

        #emit code that load the name in the stack
        self.pushConstant(MasterData(tipe=LanguageTypes.STRING, value=prop_or_method_token.literal), at_line=prop_or_method_token.line)
        line_num = self.compile(expr)#load it into stack 

        self.emitCode(op_code=OpCode.OP_GET_PROPERTY, at_line=line_num)

        return line_num


    def visitClassStatement(self, class_statement):

        class_identifier_expression = class_statement.class_identifier_expression
        function_statements = class_statement.function_statements
        variable_statements = class_statement.variable_statements
        ##############################################################################

        class_name = class_identifier_expression.expr.literal

        class_constant = MasterData(tipe=LanguageTypes.CLASS, value=ClassObj(name=class_name))
        constructor_function_arity = 0
        class_index = self.makeConstant(constant=class_constant)

        #this is for use in the vm for indexing function table 
        class_name_constant = MasterData(tipe=LanguageTypes.STRING, value=class_name)
        class_name_constant_index = self.makeConstant(constant=class_name_constant)


          ##insert these statement at the beginning of the program so that function can be called at runtime instead at compiletime
        self.addInitializingCode(OpCode.OP_LOAD_CONSTANT, line_num=0)
        self.addInitializingCode(class_index, line_num=0)

        self.addInitializingCode(OpCode.OP_DEFINE_GLOBAL, line_num=0)
        self.addInitializingCode(class_name_constant_index, line_num=0)


        #########################add properties ##############################
        for variable in variable_statements: #variable = assignmentStatement 
            lvalue_name = variable.lvalue.expr.literal 
            rvalue      = variable.rvalue

            class_constant.value.setPropertyName(property_name=lvalue_name)

        self.setInsideClass(True)

        for method in function_statements:
            
            method_name = method.function_identifier_expression.expr.literal
            
            if method_name == class_name: #this is the constructor
                constructor_function_arity = len(method.params_list)

            ip = self.getNextIPLocation()
 
            line_num = self.compile(method)
            
            

            method = MasterData(tipe=LanguageTypes.FUNCTION, 
                               value=FunctionObject(name=method_name,
                                                    arity=len(method.params_list),
                                                    ip=ip,
                                                    ))

            class_constant.value.setMethodName(method_name=method_name, method=method)


        self.setInsideClass(False)

        #set the arity of the class
        class_constant.value.arity=constructor_function_arity

        return line_num