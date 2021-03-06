from ByteArray import Chunk
from opcodes import OpCode
from lexer import TokenType
from values import LanguageTypes, MasterData
import LanguageConstants

#helper class to manage local variable in program stack
class ScopeEntity:
	def __init__(self, name, scope_depth):
		self.name = name #name is for resolving, finding variable by equating
		self.scope_depth = scope_depth# scope depth is for popping the value when scope is ended
		#p


class Compiler:
	def __init__(self):
		self.chunk = Chunk()

		self.scope_depth = 0
		self.scope_entities = []# position of ScopeEntity is the position of the variable in the stack, enumerate(scapepositoin) => (stack_index, scope_entitiy)
		self.variable_in_scope = 0 #this is for calculating the number of times we need to pop, to remove the local variable from stack


	def compileAll(self, AST):
		for AS in AST:
			self.compile(AS)

	def compile(self, AS):
		# if AS is not None:
		return AS.linkVisitor(self)

	def makeConstant(self, constant):
		return self.chunk.makeConstant(constant)

	def emitCode(self, op_code, at_line):
		self.chunk.pushOpCode(op_code, at_line)

	def emitByte(self, byte, at_line):
		self.emitCode(byte, at_line)

	def emitByteAt(self, byte, index):
		self.chunk.pushOpCodeAt(byte, index)

	def emitCodes(self, op_code1, op_code2, at_line):
		self.chunk.pushOpCodes(op_code1, op_code2, at_line)

	def pushConstant(self, constant, at_line):
		self.chunk.pushConstant(constant, at_line)

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
		elif (literal_expression.expr.tipe is TokenType.IDENTIFIER):
			
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
			self.emitCode(OpCode.OP_POP, at_line=line_num)
			return line_num

	def visitPrintStatement(self, print_statement):
		# the follwing conditition check allows print statement without any expression as having no effect
		if print_statement.expr:
			line_num = self.compile(print_statement.expr)
			self.emitCode(OpCode.OP_PRINT, at_line=line_num)
			return line_num

	def visitBlockStatement(self, block_statement):
		self.beginScope()
		line_num = 0
		for statement in block_statement.statements:
			line_num = self.compile(statement)
		self.endScope(line_num)
		return line_num


	def beginScope(self):
		self.scope_depth += 1
		
	def endScope(self, line_num):
		self.scope_depth -= 1
		# this is for calculating the number of times we need to pop, to remove the local variable from stack
		while len(self.scope_entities)!=0 and self.scope_entities[-1].scope_depth > self.scope_depth:
			self.emitCode(OpCode.OP_POP, at_line=line_num)
			self.scope_entities.pop()

			

	def visitAssignmentStatement(self, assignment_statement):
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
		return self.scope_depth>0

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

		scope_entity = ScopeEntity(name=lvalue_name, scope_depth=self.scope_depth)
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

		for stack_index, scope_entity in reversed(list(enumerate(self.scope_entities))):
			if scope_entity.name == var_name:
				# print('ressolved ', var_name)
				return stack_index
		return None

	def addScopeEntity(self, scope_entity):
		self.scope_entities.append(scope_entity)

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

			self.emitByteAt(byte=offset_if, index=branch_if_start_instruction_pointer)# update the None byte to offset

			return if_line_num

		else:

			self.emitCode(OpCode.OP_JMP, at_line=if_line_num)#we put this jump statement so that if the condition is true, the code executes as usual and jump unconditionally after reaching the end of true block, it needs to jump by amount of size of else block.
			self.emitByte(None, at_line=if_line_num) # just some random byte, we'll fill it up with true value one the 
			

			branch_if_end_instruction_pointer = self.getInstructionPointerSize()-1 #points to above byte

			offset_if = branch_if_end_instruction_pointer - branch_if_start_instruction_pointer # the number of additional line pushed in the codes stack

			self.emitByteAt(byte=offset_if, index=branch_if_start_instruction_pointer)# update the None byte to offset

			
			else_line_num = self.compile(if_statement.else_block_statement)
		
			branch_else_end_instruction_pointer = self.getInstructionPointerSize()-1

			offset_else = branch_else_end_instruction_pointer - branch_if_end_instruction_pointer
			
			self.emitByteAt(byte=offset_else, index=branch_if_end_instruction_pointer)# push offset to the end of true statement's end
			
			return else_line_num

	def visitWhileStatement(self, while_statement):
		top_label_instruction_pointer = self.getInstructionPointerSize() # this points to below expression
		line_num = self.compile(while_statement.expression) # put the condition expression in the stack

		self.emitCodes(OpCode.OP_JMP_IF_FALSE, None, at_line=line_num) #put random byte at the jump location
		branch_if_start_instruction_pointer = self.getInstructionPointerSize() - 1 # this indexes the above Null byte 

		#compile loop code 

		loop_line_num = self.compile(while_statement.block_statement)
		branch_if_end_instruction_pointer = self.getInstructionPointerSize() + 1 + 1 # this points to the following op_jmp, but we need to add one since loop ofset variable is also in the code stack and an additional 1 so that the ip_counter point next to it.

		loop_offset = top_label_instruction_pointer - branch_if_end_instruction_pointer  # this is negative, as we need to go upward
		self.emitCodes(OpCode.OP_JMP, loop_offset, at_line=loop_line_num) # this loops to the start o the top_level_counter
		
		false_condition_instruction_pointer = self.getInstructionPointerSize() - 1 #this points to the instruction after the above OP_JMP
		false_offset = false_condition_instruction_pointer - branch_if_start_instruction_pointer
		self.emitByteAt(byte=false_offset, index=branch_if_start_instruction_pointer)



