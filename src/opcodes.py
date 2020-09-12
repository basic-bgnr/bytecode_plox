from enum import Enum, auto


class OpCode(Enum):
	OP_RETURN = auto(),
	OP_LOAD_CONSTANT = auto(),
	
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

	OP_POP = auto(),
	OP_PUSH = auto(),

	OP_DEFINE_GLOBAL = auto(),
	OP_LOAD_GLOBAL = auto(),
	OP_REDEFINE_GLOBAL = auto(),

	OP_LOAD_LOCAL = auto(),
	OP_SET_LOCAL = auto(),


	OP_JMP_IF_FALSE = auto(),
	OP_JMP = auto(),

	OP_CALL = auto(),
	OP_RET = auto(),

	OP_SET_EBX = auto(),
	OP_LOAD_EBX = auto(),

	OP_GOTO =auto(),

	OP_SET_PROPERTY = auto(),
	OP_GET_PROPERTY = auto(),