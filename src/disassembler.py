from opcodes import OpCode

class Disassembler:
    def __init__(self, chunk):
        self.chunk = chunk


    def disassemble(self):
        return_string = ''
        op_code_iterator = zip(iter(self.chunk.codes), iter(self.chunk.lines))

        try:

            while ( val := next(op_code_iterator) ):
                current_opcode, current_line = val
                
                if (current_opcode == OpCode.OP_RETURN):
                    return_string += self.toString(current_line, "OP_RETURN")

                elif (current_opcode == OpCode.OP_CONSTANT):
                    index, current_line = next(op_code_iterator) #consume the next value of the code that contains the index of the constant
                    value = self.chunk.constantAt(index)
                    return_string += self.toString(current_line, f"OP_CONSTANT {value}")


                elif (current_opcode == OpCode.OP_ADD):
                    return_string += self.toString(current_line, "OP_ADD")

                elif (current_opcode == OpCode.OP_SUB):
                    return_string += self.toString(current_line, "OP_SUB")

                elif (current_opcode == OpCode.OP_MUL):
                    return_string += self.toString(current_line, "OP_MUL")

                elif (current_opcode == OpCode.OP_DIV):
                    return_string += self.toString(current_line, "OP_DIV")

                elif (current_opcode == OpCode.OP_NEG):
                    return_string += self.toString(current_line, "OP_NEG")

        except StopIteration:
            pass

        return return_string


    def toString(self, line_number, op_code):
        return f"{line_number:04} {op_code}\n"