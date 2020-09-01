from ByteArray import Chunk
from opcodes import OpCode
from lexer import TokenType
from values import LanguageTypes, MasterData
import LanguageConstants

#helper class to manage local variable in program stack
class ScopeEntity:
	def __init__(self, name, scope_depth):
		self.name = name
		self.scope_depth = scope_depth


class Compiler:
	def __init__(self):
		self.chunk = Chunk()

		self.scope_depth = 0
		self.scope_entities = []
		self.variable_in_scope = 0 #this is for calculating the number of times we need to pop, to remove the local variable from stack


	def compileAll(self, AST):
		for AS in AST:
			self.compile(AS)

	def compile(self, AS):
		return AS.linkVisitor(self)

	def visitLiteralExpression(self, literal_expression):

		if (literal_expression.expr.tipe is TokenType.NUMBER):
			
			number = MasterData(tipe= LanguageTypes.NUMBER, value = literal_expression.value)
			self.chunk.pushConstant(number, at_line = literal_expression.expr.line)

		elif (literal_expression.expr.tipe is TokenType.TRUE):			
			self.chunk.pushConstant(LanguageConstants.TRUE, at_line = literal_expression.expr.line)

		elif (literal_expression.expr.tipe is TokenType.FALSE):
			self.chunk.pushConstant(LanguageConstants.FALSE, at_line = literal_expression.expr.line)

		elif (literal_expression.expr.tipe is TokenType.NIL):
			self.chunk.pushConstant(LanguageConstants.NIL, at_line = literal_expression.expr.line)

		elif (literal_expression.expr.tipe is TokenType.STRING):

			string = MasterData(tipe= LanguageTypes.STRING, value = literal_expression.value)
			self.chunk.pushConstant(string, at_line = literal_expression.expr.line)

		##todo: identifier_token implementation 
		elif (literal_expression.expr.tipe is TokenType.IDENTIFIER):
			
			local_variable_index = self.resolveLocalVariable(literal_expression.expr.literal)
			if (local_variable_index is not None):
				self.chunk.pushOpCodes(OpCode.OP_LOAD_LOCAL, local_variable_index, at_line=literal_expression.expr.line)
			else:
				variable_name = MasterData(tipe=LanguageTypes.STRING, value=literal_expression.expr.literal)

				# self.chunk.pushConstant(string, at_line = literal_expression.expr.line)

				# lvalue_name = MasterData(tipe=LanguageTypes.STRING, value=assignment_statement.lvalue.expr.literal)

				global_variable_index = self.chunk.makeConstant(variable_name)
				
				# self.chunk.push(OpCode.OP_LOAD_GLOBAL, at_line=line_num)
				# self.chunk.push(global_variable_index, at_line=line_num)

				self.chunk.pushOpCodes(OpCode.OP_LOAD_GLOBAL, global_variable_index, at_line=literal_expression.expr.line)

		else: 
			raise Exception("no code for value other than number")

		return literal_expression.expr.line

	def visitUnaryExpression(self, unary_expression):
		literal_expression = unary_expression.right
		operator = unary_expression.operator

		line_num = self.compile(literal_expression)

		if (operator.tipe == TokenType.MINUS):
			self.chunk.pushOpCode(OpCode.OP_NEG, at_line=operator.line)
		elif(operator.tipe == TokenType.BANG):
			self.chunk.pushOpCode(OpCode.OP_NOT, at_line=operator.line)

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
			self.chunk.pushOpCode(OpCode.OP_ADD, at_line = operator.line)

		elif (operator.tipe == TokenType.MINUS):
			self.chunk.pushOpCode(OpCode.OP_SUB, at_line = operator.line)

		elif (operator.tipe == TokenType.STAR):
			self.chunk.pushOpCode(OpCode.OP_MUL, at_line = operator.line)

		elif (operator.tipe == TokenType.SLASH):
			self.chunk.pushOpCode(OpCode.OP_DIV, at_line = operator.line)

		elif (operator.tipe == TokenType.AND):
			self.chunk.pushOpCode(OpCode.OP_AND, at_line = operator.line)

		elif (operator.tipe == TokenType.OR):
			self.chunk.pushOpCode(OpCode.OP_OR, at_line = operator.line)

		elif (operator.tipe == TokenType.EQUAL_EQUAL):
			self.chunk.pushOpCode(OpCode.OP_EQUAL, at_line = operator.line)
		###################################################	
		elif (operator.tipe == TokenType.BANG_EQUAL):
			self.chunk.pushOpCode(OpCode.OP_EQUAL, at_line = operator.line)
			self.chunk.pushOpCode(OpCode.OP_NOT, at_line = operator.line)

		###################################################	
		elif (operator.tipe == TokenType.LESS):
			self.chunk.pushOpCode(OpCode.OP_LESS, at_line = operator.line)

		elif (operator.tipe == TokenType.LESS_EQUAL):
			self.chunk.pushOpCode(OpCode.OP_LESS_EQUAL, at_line = operator.line)

		elif (operator.tipe == TokenType.GREATER):
			self.chunk.pushOpCode(OpCode.OP_GREATER, at_line = operator.line)

		elif (operator.tipe == TokenType.GREATER_EQUAL):
			self.chunk.pushOpCode(OpCode.OP_GREATER_EQUAL, at_line = operator.line)

		return line_num



	def GroupingExpression(self, grouping_expression):
		return self.compile(grouping_expression.expression)

	def visitExpressionStatement(self, expression_statement):
		#to do check case for null statement
		#the following conditional is for global_variable
		
		if expression_statement.expr:
			#to do: use line_num
			line_num = self.compile(expression_statement.expr)
			self.chunk.pushOpCode(OpCode.OP_POP, at_line=line_num)
			return line_num

	def visitPrintStatement(self, print_statement):
		# the follwing conditition check allows print statement without any expression as having no effect
		if print_statement.expr:
			line_num = self.compile(print_statement.expr)
			self.chunk.pushOpCode(OpCode.OP_PRINT, at_line=line_num)
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
			self.chunk.pushOpCode(OpCode.OP_POP, at_line=line_num)
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

		global_variable_index = self.chunk.makeConstant(lvalue_name)
		self.chunk.pushOpCodes(OpCode.OP_REDEFINE_GLOBAL, global_variable_index, at_line=line_num)
		return line_num

	def addGlobalAssignment(self, assignment_statement):
		line_num = self.compile(assignment_statement.rvalue) # this pushes rvalue in the program stack
		lvalue_name = MasterData(tipe=LanguageTypes.STRING, value=assignment_statement.lvalue.expr.literal)

		global_variable_index = self.chunk.makeConstant(lvalue_name)#make the lvalue into MasterData and store it in the constant table
		self.chunk.pushOpCodes(OpCode.OP_DEFINE_GLOBAL, global_variable_index, at_line=line_num)
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
			self.chunk.pushOpCodes(OpCode.OP_SET_LOCAL, local_stack_index, at_line=line_num)
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
