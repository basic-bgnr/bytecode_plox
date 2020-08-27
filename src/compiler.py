from ByteArray import Chunk
from opcodes import OpCode
from lexer import TokenType

class Compiler:
	def __init__(self):
		self.chunk = Chunk()

	def compile(self, expression):
		expression.linkVisitor(self)

	def visitLiteralExpression(self, literal_expression):
		if (literal_expression.expr.tipe in [TokenType.NUMBER]):
			constant = literal_expression.value 
			self.chunk.pushConstant(constant, at_line = literal_expression.expr.line)
		else:
			raise Exception("no code for value other than number")

	def visitUnaryExpression(self, unary_expression):
		value = unary_expression.right
		operator = unary_expression.operator

		self.compile(value)

		if (operator.tipe == TokenType.MINUS):
			self.chunk.push(OpCode.OP_NEG, at_line=operator.line)

	def visitBinaryExpression(self, binary_expression):
		right = binary_expression.right
		left  = binary_expression.left
		operator = binary_expression.operator

		# here the order in which the following two expr is compiled to important when 
		# popping the value for calculation in the virtual machine
		self.compile(right)
		self.compile(left)
		

		if (operator.tipe == TokenType.PLUS):
			self.chunk.push(OpCode.OP_ADD, at_line = operator.line)

		if (operator.tipe == TokenType.MINUS):
			self.chunk.push(OpCode.OP_SUB, at_line = operator.line)

		if (operator.tipe == TokenType.STAR):
			self.chunk.push(OpCode.OP_MUL, at_line = operator.line)

		if (operator.tipe == TokenType.SLASH):
			self.chunk.push(OpCode.OP_DIV, at_line = operator.line)

	def GroupingExpression(self, grouping_expression):
		self.compile(grouping_expression.expression)

	def visitExpressionStatement(self, expression_statement):
		self.compile(expression_statement.expr)