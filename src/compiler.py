from ByteArray import Chunk
from opcodes import OpCode
from lexer import TokenType
from values import LanguageTypes, MasterData
import LanguageConstants

class Compiler:
	def __init__(self):
		self.chunk = Chunk()

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
		if expression_statement.expr:
			#to do: use line_num
			line_num = self.compile(expression_statement.expr)
			self.chunk.pushOpCode(OpCode.OP_POP, at_line=line_num)

	def visitPrintStatement(self, print_statement):
		# the follwing conditition check allows print statement without any expression as having no effect
		if print_statement.expr:
			line_num = self.compile(print_statement.expr)
			self.chunk.pushOpCode(OpCode.OP_PRINT, at_line=line_num)

	def visitAssignmentStatement(self, assignment_statement):
		line_num = self.compile(assignment_statement.rvalue)

		##find out the lvalue string and enter it inside the chunk constant pool
		lvalue_name = MasterData(tipe=LanguageTypes.STRING, value=assignment_statement.lvalue.expr.literal)

		global_variable_index = self.chunk.makeConstant(lvalue_name)
		
		# self.chunk.push(OpCode.OP_DEFINE_GLOBAL, at_line=line_num)
		# self.chunk.push(global_variable_index, at_line=line_num)


		self.chunk.pushOpCodes(OpCode.OP_DEFINE_GLOBAL, global_variable_index, at_line=line_num)


