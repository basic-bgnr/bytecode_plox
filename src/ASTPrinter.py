from lexer import TokenType
class ASTPrinter:
    #statement are enclosed in <>
    def printAll(self, entities):
        return '\n'.join([self.print(entity) for entity in entities])

    def print(self, entity):
        return entity.linkVisitor(self)

    def visitGetExpression(self, get_expression):
        return f"(get {self.print(get_expression.expr)}.{get_expression.prop_or_method.literal})"

    def visitClassStatement(self, class_statement):
        ret_val = f"{class_statement.name} {self.print(class_statement.class_identifier_expression)}" + '{\n'
        ret_val += '\n'.join([self.print(variable) for variable in class_statement.variable_statements]) + '\n'
        ret_val += '\n'.join([self.print(function) for function in class_statement.function_statements])
        ret_val += '\n}'
        return ret_val

    def visitReturnStatement(self, return_statement):
        ret_val = f"{return_statement.name} {self.print(return_statement.expr)}"
        return ret_val

    def visitFunctionStatement(self, function_statement):
        # print(f'insid printer->  {function_statement.params_list}')
        ret_val = "<func> " + self.print(function_statement.function_identifier_expression)
        ret_val += f"({','.join([arg.expr.literal for arg in function_statement.params_list])}) "
        ret_val += self.print(function_statement.block_statement)
        return ret_val

    def visitWhileStatement(self, while_statement):
        ret_val = while_statement.name + ' ' + self.print(while_statement.expression) + '\n'
        ret_val += self.print(while_statement.block_statement)
        return ret_val

    def visitIfStatement(self, if_statement):
        ret_val = if_statement.name1 + ' ' + self.print(if_statement.expression) +'\n'
        ret_val += self.print(if_statement.if_block_statement) + '\n'
        if (else_block_statement := if_statement.else_block_statement):
            ret_val += if_statement.name2 + '\n' 
            ret_val += self.print(else_block_statement)
        return ret_val

    def visitBlockStatement(self, block_statement):
        ret_val = block_statement.name + "{\n"
        for statement in block_statement.statements:
            ret_val += self.print(statement) + '\n'
        ret_val += '}'
        return ret_val

    def visitAssignmentStatement(self, statement):
        #below statement.lvalue.literal is used since statement.lvalue.lexeme contains entire alphanumeric characters
        ret_val = f"{statement.name} {self.print(statement.lvalue)}, {self.print(statement.rvalue)}"
        return ret_val

    def visitReassignmentStatement(self, statement):
        ret_val = f"{statement.name} {self.print(statement.lvalue)}, {self.print(statement.rvalue)}"
        return ret_val

    def visitPrintStatement(self, statement): 
        # print('AST')
        ret_val  = f"{statement.name} {self.print(statement.expr)}"
        # print(ret_val)
        return ret_val

    def visitExpressionStatement(self, statement):
        return f"{statement.name} {self.print(statement.expr)}"

    def visitBinaryExpression(self, binary_expression):
        return self.parenthesize(binary_expression.operator.lexeme,
                                binary_expression.left,
                                binary_expression.right)

    def visitGroupingExpression(self, grouping_expression):
        return self.parenthesize('group',
                                grouping_expression.expression)

    def visitUnaryExpression(self, unary_expression):
        return self.parenthesize(unary_expression.operator.lexeme,
                                unary_expression.right)

    def visitCallableExpression(self, callable_expression):
        return self.parenthesize(self.print(callable_expression.caller_expr), *callable_expression.args)

    def visitLiteralExpression(self, literal_expression):
        if (literal_expression.expr.tipe in [TokenType.NUMBER, TokenType.STRING, TokenType.IDENTIFIER]):
            return str(literal_expression.value)
        return literal_expression.expr.lexeme


    def parenthesize(self, operator, *expressions):
        recursive_values =  ' '.join([self.print(expression) for expression in expressions])
        return f"({operator} {recursive_values})"