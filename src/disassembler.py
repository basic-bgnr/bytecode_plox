from opcodes import OpCode
from itertools import count
class Disassembler:
    def __init__(self, chunk, initializing_codes):
        self.chunk = chunk
        self.initializing_codes = initializing_codes


    def disassemble(self):
        NotImplemented

    def pretty_print(self):

        initializing_codes = self.formatOpCodes(header='INITIALIZING_CODES', chunk=self.initializing_codes.codes)
        program_code       = self.formatOpCodes(header='PROGRAM_CODE', chunk=self.chunk.codes)

        constant_pool = Disassembler.stringifyConstantPool(header='CONSTANT POOL', constant_pool=self.chunk.constants)


        return '\n'.join(constant_pool + initializing_codes + program_code)


    def formatOpCodes(self, header, chunk):
        output_string = [f"{header:^50}"]
        # line_code_pair = zip(self.chunk.lines, self.chunk.codes)
        line_code_pair = zip(count(0, 1), chunk)


        op_codes_followed_by_bytes = [OpCode.OP_LOAD_CONSTANT, 
                                     OpCode.OP_DEFINE_GLOBAL,
                                     OpCode.OP_LOAD_GLOBAL,
                                     OpCode.OP_REDEFINE_GLOBAL,
                                     OpCode.OP_LOAD_LOCAL,
                                     OpCode.OP_SET_LOCAL,
                                     OpCode.OP_JMP_IF_FALSE,
                                     OpCode.OP_JMP,
                                     #OpCode.OP_CALL,
                                     OpCode.OP_PUSH,
                                     OpCode.OP_GOTO]
                         
        ###############################################
        op_codes_stack  = [OpCode.OP_LOAD_LOCAL,
                           OpCode.OP_SET_LOCAL,
                           OpCode.OP_JMP_IF_FALSE,
                           OpCode.OP_JMP,
                           #OpCode.OP_CALL,
                           OpCode.OP_PUSH,
                           OpCode.OP_GOTO]

        op_codes_global = [OpCode.OP_LOAD_CONSTANT, 
                         OpCode.OP_DEFINE_GLOBAL,
                         OpCode.OP_LOAD_GLOBAL,
                         OpCode.OP_REDEFINE_GLOBAL,
                         ]

        ###############################################
        # list(map(lambda x: print(x), [str(c) for c in self.chunk.codes]))
        for line_number, op_code in line_code_pair:

            if op_code in op_codes_followed_by_bytes:
                _, next_byte = next(line_code_pair)

                value = self.constantAt(index=next_byte) if op_code in op_codes_global else '[...]'

                output_string.append(Disassembler.stringifyOpCode(line_number , op_code, f"[{next_byte}]", value))
            else:
                output_string.append(Disassembler.stringifyOpCode(line_number, op_code))

        return output_string

    @staticmethod
    def stringifyOpCode(line_number, op_code, *options):
        optional_string = ""
        for option in options:
            optional_string += f" {str(option):<10}"

        return f"{line_number:>04} {op_code.name:<18} {optional_string:>2}"

        # return f" {str(line_number)}   {str(op_code)}  {optional_string}"

    @staticmethod
    def stringifyConstantPool(header, constant_pool):
        output_string = [f"{header:^50}"]
        for index, constant in enumerate(constant_pool):
            output_string.append(f"{index}. {constant}")
        return output_string


    def constantAt(self, index):
        return self.chunk.constantAt(index)