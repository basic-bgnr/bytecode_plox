from enum import Enum, auto


class OpCode(Enum):
	OP_RETURN = auto(),
	OP_CONSTANT = auto(),
	
	OP_ADD = auto(),
	OP_SUB = auto(),
	OP_MUL = auto(),
	OP_DIV = auto(),
	OP_NEG = auto(),

	OP_EQUAL = auto(),
	OP_LESS = auto(),
	OP_GREATER  = auto(),
	OP_LESS_EQUAL = auto(),
	OP_GREATER_EQUAL  = auto(),

	OP_AND = auto(),
	OP_OR  = auto(),

	OP_NOT = auto(),

	OP_PRINT = auto(),

	OP_POP = auto()

	OP_DEFINE_GLOBAL = auto(),
	OP_LOAD_GLOBAL = auto(),