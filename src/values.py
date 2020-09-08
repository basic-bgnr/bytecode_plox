from enum import Enum, auto

class LanguageTypes(Enum):
	NUMBER = auto(),
	BOOLEAN = auto(),
	NULL = auto()
	STRING = auto(),
	FUNCTION = auto(),

class MasterData:
	def __init__(self, tipe, value):
		self.tipe = tipe 
		self.value = value # when encoding into c types value is of enum {number, boolean}

	def __str__(self):
		if self.tipe == LanguageTypes.STRING:
			return f'"{self.value}">'
		if self.tipe == LanguageTypes.FUNCTION:
			return f"<{self.tipe.name} {self.value}>"

		return f"{self.value}"

	###############optimization for low memory count during compilation, if any error comment out the following########
	def __hash__(self):
		if self.tipe == LanguageTypes.STRING:
			return hash(self.value)
		else:
			return hash((self.tipe, self.value))

	def __eq__(self, other):
		return self.value == other.value

class FunctionObject:
	def __init__(self, name, arity, ip):
		self.name = name 
		self.arity = arity
		self.ip = ip  

	def __str__(self):
		return f"{self.name}"