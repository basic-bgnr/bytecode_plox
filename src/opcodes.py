from enum import Enum, auto


class OpCode(Enum):
	OP_RETURN = auto(),
	OP_CONSTANT = auto(),
	
	OP_ADD = auto(),
	OP_SUB = auto(),
	OP_MUL = auto(),
	OP_DIV = auto(),
	OP_NEG = auto(),
