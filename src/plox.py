import sys
from lexer import Scanner
from parser import Parser

from ASTPrinter import ASTPrinter
from compiler import Compiler 

from disassembler import Disassembler

from vm import Vm

class Lox:
    prompt_signature = '#>>'
        
    @staticmethod
    def main():
        if len(sys.argv) > 2:
            if (sys.argv[2] == '-i'):
                Lox.runFileInteractive(sys.argv[1], Vm())
            else:
                print('''usage: 
                    plox files [-i]
                    -i: run files in interactive mode''')
            exit(64) #see open_bsd exit code (just for standardization)
        elif len(sys.argv) == 2:
            # Lox.runFile(sys.argv[1], Vm())
            Lox.runDebugFile(sys.argv[1], Vm())

        else:
            # Lox.runPrompt(Vm())
            Lox.runDebugPrompt(Vm())

    @staticmethod
    def runFileInteractive(path, vm):
        Lox.runFile(path, vm)
        Lox.runPrompt(vm)

    @staticmethod
    def runDebugFile(path, vm):
        with open(path, mode='r') as content:
            source_code = content.read()
            Lox.debugRun(source_code, vm)

    @staticmethod
    def runFile(path, vm):
        with open(path, mode='r') as content:
            source_code = content.read()
            Lox.run(source_code, vm)
            # Lox.debugRun(source_code, vm)
        ### add interpreter in prompt mode after this. if necessary arguments are passed
    
    @staticmethod
    def runPrompt(vm):
        while True:
            print(Lox.prompt_signature, end=' ')
            try:
                input_source = input()
                Lox.run(input_source, vm)
            except Exception as e: 
                print(f"{e}")

    @staticmethod
    def runDebugPrompt(vm):
        while True:
            print(Lox.prompt_signature, end=' ')
            input_source = input()
            Lox.debugRun(input_source, vm)
            
    @staticmethod
    def run(source_code, vm):
        #why this runs, its because of the lox interpreter environment, which remains in existence even after this function ends 
        scanner = Scanner(source_code)
        scanner.scanTokens()
        
        parser = Parser(scanner.token_list)
        parser.parse()

        compiler = Compiler()
        entry_point = compiler.compileAll(parser.AST)

        disassembler = Disassembler(compiler.chunk, compiler.initializing_codes)
       
        vm.run(compiler.chunk, initializing_codes=compiler.initializing_codes, start_at = 0)
        

    @staticmethod
    def debugRun(source_code, vm):
        #why this runs, its because of the lox interpreter environment, which remains in existence even after this function ends 
        scanner = Scanner(source_code)
        scanner.scanTokens()
        
        print(scanner.toString())
        
        parser = Parser(scanner.token_list)
        parser.parse()

        print("##################################AST###################################")
        print(ASTPrinter().printAll(parser.AST))
        print("########################################################################")
        compiler = Compiler()
        entry_point = compiler.compileAll(parser.AST)

        print('entry point ', entry_point)

        disassembler = Disassembler(compiler.chunk, compiler.initializing_codes)
        print("#############################ByteCode###################################")
        print(disassembler.pretty_print())
        print("########################################################################")

        import time
        a = time.time()
        vm.run(compiler.chunk, initializing_codes=compiler.initializing_codes, start_at = 0)
        
        print("########################################################################")
        print('time ', time.time() -a)

#run the program by calling the static function main of the interpreter
Lox.main()
