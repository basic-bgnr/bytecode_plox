from enum import Enum, auto

class LanguageTypes(Enum):
	NUMBER          = auto(),
	BOOLEAN         = auto(),
	NULL            = auto()
	STRING          = auto(),
	FUNCTION        = auto(),
	NATIVE_FUNCTION = auto(),
	CLASS           = auto(),
	INSTANCE        = auto(),

class MasterData:
	def __init__(self, tipe, value):
		self.tipe = tipe 
		self.value = value # when encoding into c types value is of enum {number, boolean}

	def __str__(self):
		if self.tipe == LanguageTypes.STRING:
			return f'"{self.value}"'

		if self.tipe in [LanguageTypes.FUNCTION, LanguageTypes.NATIVE_FUNCTION, LanguageTypes.CLASS, LanguageTypes.INSTANCE]:
			return f"<{self.tipe.name} {self.value}>"

		return f"{self.value}"
		# return f"MasterData tipe: <{self.tipe.name}> value: [{self.value}]"
	###############optimization for low memory count during compilation, if any error comment out the following########
	def __hash__(self):
		if self.tipe == LanguageTypes.STRING:
			return hash(self.value)
		else:
			return hash((self.tipe, self.value))

	def __eq__(self, other):
		return self.value == other.value

class FunctionObject:
	def __init__(self, name, arity, ip, instance=None):
		self.name = name 
		self.arity = arity
		self.ip = ip
		self.instance= instance #link instance 

	def setInstance(self, instance):
		self.instance = instance

	def getInstance(self):
		return self.instance

	def __str__(self):
		return f"{self.name}"

class NativeFunctionObject:
	def __init__(self, name, arity, ip=None):
		self.name = name 
		self.arity = arity

		self.ip = ip
		self.function = None

	def setFunction(self, function):
		self.function = function 

	def call(self, *args):
		return self.function(*args)

	def __str__(self):
		return f"{self.name}"


class ClassObj:
	def __init__(self, name, arity=0):
		self.name  = name
		self.arity = arity

		self.property_names = [] #this is list
		self.method_objects = {} #this is dict

	def getProperty(self, method_name): # this is called by vm 
		method = self.getMethod(method_name=method_name)
		method.value.setInstance(MasterData(tipe=LanguageTypes.CLASS, value=self))
		return method

	def getMethod(self, method_name):
		return self.method_objects[method_name]

	def getPropertyNames(self):
		return self.property_names

	def setMethodName(self, method_name, method):
		self.method_objects[method_name] = method

	def setPropertyName(self, property_name):
		self.property_names.append(property_name)

	def call(self, *args):
		return MasterData(tipe=LanguageTypes.INSTANCE, value=InstanceObj(class_=self))

	def __str__(self):
		return f"{self.name}"

class InstanceObj:
	def __init__(self, class_):
		self.class_ = class_
		
		self.properties = {}

	#to do: this is hacky, optimize 
	def getProperty(self, value):
		try:
			method = self.class_.getMethod(method_name=value)
			method.value.setInstance(MasterData(tipe=LanguageTypes.INSTANCE, value=self))
			return method
		except KeyError:#if method is not found try property
			return self.properties[value]


	def __str__(self):
		return f"{self.class_}"