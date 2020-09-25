from values import LanguageTypes, MasterData, NativeFunctionObject, FunctionObject, ClassObj, InstanceObj

from enum import Enum

###for native functionality only 
import time
import random

class NativeModules(Enum):
    NUMBER  = 'Number',
    RANDOM  = 'Random',
    STRING  = 'String',
    TIME    = 'Time',
    RUNTIME = 'Runtime',
    IO      = 'IO',


class NativeFunctions(Enum):
    INT    = 'int',
    STR    = 'str',
    TIME   = 'time',
    RANDOM = 'random',
    TYPE   = 'type',
    EXIT   = 'exit',

class RuntimeFunctions(Enum):
    GETPROPERTY = 'getProperty',
    SETPROPERTY = 'setProperty',

class StringFunctions(Enum):
    AT     = 'at',
    CHUNK  = 'chunk',
    LENGTH = 'length',

class IOFunctions(Enum):
    READFILE = 'readFile',
    WRITEFILE = 'writeFile',



class NativeModuleGenerator:

    @staticmethod    
    def generateAll():
        module_table = {}

        all_modules = [NativeModuleGenerator.generateNumberModule(),
                       NativeModuleGenerator.generateRandomModule(),
                       NativeModuleGenerator.generateStringModule(),
                       NativeModuleGenerator.generateTimeModule(),
                       NativeModuleGenerator.generateRuntimeModule(),
                       NativeModuleGenerator.generateIOModule(),]

        # number_module = NativeModuleGenerator.generateNumberModule()
        # random_module = NativeModuleGenerator.generateRandomModule()
        # string_module = NativeModuleGenerator.generateStringModule()
        # time_module   = NativeModuleGenerator.generateTimeModule()

        for module in all_modules:
            module_table[module.value.name] = module

        return module_table 



    @staticmethod
    def generateNumberModule():

        NUMBER_CLASS = MasterData(tipe=LanguageTypes.CLASS, value=ClassObj(name=NativeModules.NUMBER.value[0]))

        INT_FUNCTION_IDENTIFIER = NativeFunctions.INT.value[0]
        INT_FUNCTION = NativeFunctionObject(name=INT_FUNCTION_IDENTIFIER, arity=1)
        INT_FUNCTION.setFunction(lambda x: MasterData(tipe=LanguageTypes.NUMBER, value=int(x.value)))

        NUMBER_CLASS.value.setMethodName(method_name=INT_FUNCTION_IDENTIFIER, method= MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=INT_FUNCTION))


        return NUMBER_CLASS

    @staticmethod
    def generateRandomModule():

        RANDOM_CLASS = MasterData(tipe=LanguageTypes.CLASS, value=ClassObj(name=NativeModules.RANDOM.value[0]))


        RANDOM_FUNCTION_IDENTIFIER = NativeFunctions.RANDOM.value[0]
        RANDOM_FUNCTION = NativeFunctionObject(name=RANDOM_FUNCTION_IDENTIFIER, arity=0)
        RANDOM_FUNCTION.setFunction(lambda: MasterData(tipe=LanguageTypes.NUMBER, value=random.random()))

        RANDOM_CLASS.value.setMethodName(method_name=RANDOM_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=RANDOM_FUNCTION))


        return RANDOM_CLASS

    @staticmethod
    def generateTimeModule():

        TIME_CLASS = MasterData(tipe=LanguageTypes.CLASS, value=ClassObj(name=NativeModules.TIME.value[0]))

        TIME_FUNCTION_IDENTIFIER = NativeFunctions.TIME.value[0]
        TIME_FUNCTION = NativeFunctionObject(name=TIME_FUNCTION_IDENTIFIER, arity=0)
        TIME_FUNCTION.setFunction(lambda: MasterData(tipe=LanguageTypes.NUMBER, value=time.time_ns()))

        TIME_CLASS.value.setMethodName(method_name=TIME_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=TIME_FUNCTION))


        return TIME_CLASS

    @staticmethod
    def generateStringModule():

        STRING_CLASS = MasterData(tipe=LanguageTypes.CLASS, value=ClassObj(name=NativeModules.STRING.value[0]))
        
        STR_FUNCTION_IDENTIFIER = NativeFunctions.STR.value[0]
        STR_FUNCTION = NativeFunctionObject(name=STR_FUNCTION_IDENTIFIER, arity=1)
        STR_FUNCTION.setFunction(lambda x: MasterData(tipe=LanguageTypes.STRING, value=str(x.value)))

        AT_FUNCTION_IDENTIFIER = StringFunctions.AT.value[0]
        AT_FUNCTION = NativeFunctionObject(name=AT_FUNCTION_IDENTIFIER, arity=2)
        AT_FUNCTION.setFunction(lambda obj, index: MasterData(tipe=LanguageTypes.STRING, value=obj.value[int(index.value)]))

        CHUNK_FUNCTION_IDENTIFIER = StringFunctions.CHUNK.value[0]
        CHUNK_FUNCTION = NativeFunctionObject(name=CHUNK_FUNCTION_IDENTIFIER, arity=3)
        CHUNK_FUNCTION.setFunction(lambda obj, start, end: MasterData(tipe=LanguageTypes.STRING, value=obj.value[int(start.value):int(end.value)]))

        LENGTH_FUNCTION_IDENTIFIER = StringFunctions.LENGTH.value[0]
        LENGTH_FUNCTION = NativeFunctionObject(name=LENGTH_FUNCTION_IDENTIFIER, arity=1)
        def _length(obj):
            try:
                return MasterData(tipe=LanguageTypes.NUMBER, value=len(obj.value))
            except:
                raise Exception(f"Expecting: String, found: {obj.tipe}")
        LENGTH_FUNCTION.setFunction(_length)

        STRING_CLASS.value.setMethodName(method_name=STR_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=STR_FUNCTION))
        STRING_CLASS.value.setMethodName(method_name=AT_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=AT_FUNCTION))
        STRING_CLASS.value.setMethodName(method_name=CHUNK_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=CHUNK_FUNCTION))
        STRING_CLASS.value.setMethodName(method_name=LENGTH_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=LENGTH_FUNCTION))

        return STRING_CLASS

    @staticmethod
    def generateRuntimeModule():

        RUNTIME_CLASS = MasterData(tipe=LanguageTypes.CLASS, value=ClassObj(name=NativeModules.RUNTIME.value[0]))
        
        TYPE_FUNCTION_IDENTIFIER = NativeFunctions.TYPE.value[0]
        TYPE_FUNCTION = NativeFunctionObject(name=TYPE_FUNCTION_IDENTIFIER, arity=1)
        TYPE_FUNCTION.setFunction(lambda x: MasterData(tipe=LanguageTypes.TYPE, value=x.tipe.name))        

        EXIT_FUNCTION_IDENTIFIER = NativeFunctions.EXIT.value[0]
        EXIT_FUNCTION = NativeFunctionObject(name=EXIT_FUNCTION_IDENTIFIER, arity=1)
        EXIT_FUNCTION.setFunction(lambda x: exit(int(x.value)))


        SETPROPERTY_FUNCTION_IDENTIFIER = RuntimeFunctions.SETPROPERTY.value[0]
        SETPROPERTY_FUNCTION = NativeFunctionObject(name=SETPROPERTY_FUNCTION_IDENTIFIER, arity=3)
        def _set_property(obj, lvalue, rvalue):
            if obj.tipe == LanguageTypes.INSTANCE:
                obj.value.setProperty(lvalue.value, rvalue)
            else:
                raise Exception(f"Expecting: Instance, found: {obj.tipe}")
        SETPROPERTY_FUNCTION.setFunction(_set_property)

        GETPROPERTY_FUNCTION_IDENTIFIER = RuntimeFunctions.GETPROPERTY.value[0]
        GETPROPERTY_FUNCTION = NativeFunctionObject(name=GETPROPERTY_FUNCTION_IDENTIFIER, arity=2)
        def _get_property(obj, prop):
            if obj.tipe == LanguageTypes.INSTANCE:
                try:
                    return obj.value.getProperty(prop.value)
                except KeyError as e:
                    raise Exception(f"no property {prop} found in {obj}")
            else:
                raise Exception(f"Expecting: Instance, found: {obj.tipe}")
        GETPROPERTY_FUNCTION.setFunction(_get_property)


        RUNTIME_CLASS.value.setMethodName(method_name=TYPE_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=TYPE_FUNCTION))
        RUNTIME_CLASS.value.setMethodName(method_name=EXIT_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=EXIT_FUNCTION))
        RUNTIME_CLASS.value.setMethodName(method_name=SETPROPERTY_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=SETPROPERTY_FUNCTION))
        RUNTIME_CLASS.value.setMethodName(method_name=GETPROPERTY_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=GETPROPERTY_FUNCTION))

        return RUNTIME_CLASS


    @staticmethod
    def generateIOModule():

        IO_CLASS = MasterData(tipe=LanguageTypes.CLASS, value=ClassObj(name=NativeModules.IO.value[0]))

        READ_FUNCTION_IDENTIFIER = IOFunctions.READFILE.value[0]
        READ_FUNCTION = NativeFunctionObject(name=READ_FUNCTION_IDENTIFIER, arity=1)
        def _read(location):
            try:
                with open(location.value, 'rt', encoding='ascii') as file_handle:
                    native_string = file_handle.read()
                    return MasterData(tipe=LanguageTypes.STRING, value=native_string)
            except Exception as e:
                print 
                raise Exception(f"error while reading file {location.value} {e.args[0]}")

        READ_FUNCTION.setFunction(_read)

        WRITE_FUNCTION_IDENTIFIER = IOFunctions.WRITEFILE.value[0]
        WRITE_FUNCTION = NativeFunctionObject(name=WRITE_FUNCTION_IDENTIFIER, arity=2)
        def _write(location, string):
            try:
                with open(location.value, 'wt', encoding='ascii') as file_handle:
                    file_handle.write(string.value)
            except Exception as e:
                raise Exception(f"error while writing file {location.value} {e.args[0]}")

        WRITE_FUNCTION.setFunction(_write)

        IO_CLASS.value.setMethodName(method_name=READ_FUNCTION_IDENTIFIER, method= MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=READ_FUNCTION))
        IO_CLASS.value.setMethodName(method_name=WRITE_FUNCTION_IDENTIFIER, method= MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=WRITE_FUNCTION))


        return IO_CLASS