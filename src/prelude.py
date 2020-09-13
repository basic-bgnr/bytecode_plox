from values import LanguageTypes, MasterData, NativeFunctionObject, FunctionObject, ClassObj, InstanceObj

from enum import Enum

###for native functionality only 
import time
import random 

class NativeModules(Enum):
    NUMBER = 'Number',
    RANDOM = 'Random',
    STRING = 'String',
    TIME   = 'Time',
    RUNTIME = 'Runtime',


class NativeFunctions(Enum):
    INT    = 'int',
    STR    = 'str',
    TIME   = 'time',
    RANDOM = 'random',
    TYPE   = 'type',


class NativeModuleGenerator:

    @staticmethod    
    def generateAll():
        module_table = {}

        all_modules = [NativeModuleGenerator.generateNumberModule(),
                       NativeModuleGenerator.generateRandomModule(),
                       NativeModuleGenerator.generateStringModule(),
                       NativeModuleGenerator.generateTimeModule(),
                       NativeModuleGenerator.generateRuntimeModule(),]

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

        STRING_CLASS.value.setMethodName(method_name=STR_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=STR_FUNCTION))


        return STRING_CLASS

    @staticmethod
    def generateRuntimeModule():

        RUNTIME_CLASS = MasterData(tipe=LanguageTypes.CLASS, value=ClassObj(name=NativeModules.RUNTIME.value[0]))
        
        TYPE_FUNCTION_IDENTIFIER = NativeFunctions.TYPE.value[0]
        TYPE_FUNCTION = NativeFunctionObject(name=TYPE_FUNCTION_IDENTIFIER, arity=1)
        TYPE_FUNCTION.setFunction(lambda x: MasterData(tipe=LanguageTypes.TYPE, value=x.tipe.name))

        RUNTIME_CLASS.value.setMethodName(method_name=TYPE_FUNCTION_IDENTIFIER, method=MasterData(tipe=LanguageTypes.NATIVE_FUNCTION, value=TYPE_FUNCTION))


        return RUNTIME_CLASS