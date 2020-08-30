from opcodes import OpCode

class Disassembler:
    def __init__(self, chunk):
        self.chunk = chunk


    def disassemble(self):
        return_string = []
        op_code_iterator = zip(iter(self.chunk.codes), iter(self.chunk.lines))

        try:
            while ( val := next(op_code_iterator) ):
                current_opcode, current_line = val
                
                if (current_opcode in [OpCode.OP_CONSTANT, OpCode.OP_DEFINE_GLOBAL, OpCode.OP_LOAD_GLOBAL]):
                    index, current_line = next(op_code_iterator) #consume the next value of the code that contains the index of the constant
                    value = self.chunk.constantAt(index)
                    # print(index, "---", type(value), '---', value.value, value.tipe)
                    return_string.append( self.toString(current_line, f"{current_opcode.name}", f"[{index}]" , f"{value}" ) )
                else:
                    return_string.append( self.toString(current_line, f"{current_opcode.name}") )

        except StopIteration:
            pass

        return "\n".join(return_string)


    def toString(self, line_number, op_code, *options):
        optional_string = ""
        for option in options:
            optional_string += f" {option:>4} "

        return f"{line_number:>04} {op_code:<18}" + optional_string