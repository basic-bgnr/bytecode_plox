from opcodes import OpCode

class Disassembler:
    def __init__(self, chunk):
        self.chunk = chunk


    def disassemble(self):
        NotImplemented

    def pretty_print(self):
        output_string = []
        line_code_pair = zip(self.chunk.lines, self.chunk.codes)

        op_codes_followed_by_bytes = [OpCode.OP_LOAD_CONSTANT, 
                                     OpCode.OP_DEFINE_GLOBAL,
                                     OpCode.OP_LOAD_GLOBAL,
                                     OpCode.OP_REDEFINE_GLOBAL,
                                     OpCode.OP_LOAD_LOCAL,
                                     OpCode.OP_SET_LOCAL,
                                     OpCode.OP_JMP_IF_FALSE,
                                     OpCode.OP_JMP,
                                     OpCode.OP_RET,
                                     OpCode.OP_CALL,
                                     OpCode.OP_PUSH]
                         
        ###############################################
        op_codes_stack  = [OpCode.OP_LOAD_LOCAL,
                           OpCode.OP_SET_LOCAL,
                           # OpCode.OP_JMP_IF_FALSE,
                           OpCode.OP_JMP,
                           OpCode.OP_RET,
                           OpCode.OP_CALL,
                           OpCode.OP_PUSH]

        op_codes_global = [OpCode.OP_LOAD_CONSTANT, 
                             OpCode.OP_DEFINE_GLOBAL,
                             OpCode.OP_LOAD_GLOBAL,
                             OpCode.OP_REDEFINE_GLOBAL]

        ###############################################
        # list(map(lambda x: print(x), [str(c) for c in self.chunk.codes]))
        for line_number, op_code in line_code_pair:

            if op_code in op_codes_followed_by_bytes:
                _, next_byte = next(line_code_pair)

                value = self.constantAt(index=next_byte) if op_code in op_codes_global else '[...]'

                output_string.append(Disassembler.stringify(line_number , op_code, f"[{next_byte}]", value))
            else:
                output_string.append(Disassembler.stringify(line_number, op_code))

        return '\n'.join(output_string)

    @staticmethod
    def stringify(line_number, op_code, *options):
        optional_string = ""
        for option in options:
            optional_string += f" {str(option):<10}"

        return f"{line_number:>04} {op_code.name:<18}" + optional_string

        # return f" {str(line_number)}   {str(op_code)}  {optional_string}"

    def constantAt(self, index):
        return self.chunk.constantAt(index)