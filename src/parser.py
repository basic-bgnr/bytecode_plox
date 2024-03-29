from ASTPrinter import ASTPrinter


class ClassStatement:
    def __init__(
        self, class_identifier_expression, function_statements, variable_statements
    ):
        self.class_identifier_expression = class_identifier_expression
        self.function_statements = function_statements
        self.variable_statements = variable_statements

        ##check if class constructor is defined, raise error if not

        # class_name_token = self.class_identifier_expression.expr
        # if class_name_token.literal not in map(lambda function: function.function_identifier_expression.expr.literal, function_statements):
        #     raise Exception(f"class constructor is not defined for class {class_name_token.literal} at line {class_name_token.line}")
        # to do: check if the class constructor have return statement and raise error if it's present

        self.name = "<class>"

    def linkVisitor(self, visitor):
        return visitor.visitClassStatement(self)


########################################################
class FunctionStatement:
    def __init__(self, function_identifier_expression, params_list, block_statement):
        self.function_identifier_expression = function_identifier_expression
        self.params_list = params_list  # list of token
        self.block_statement = block_statement  # BlockStatement

        self.name = "<function>"

    def linkVisitor(self, visitor):
        return visitor.visitFunctionStatement(self)


class ReturnStatement:
    def __init__(self, expr):
        self.expr = expr
        self.name = f"<return>"

    def linkVisitor(self, visitor):
        return visitor.visitReturnStatement(self)


class ContinueStatement:
    def __init__(self, token):
        self.token = token
        self.name = f"<continue>"

    def linkVisitor(self, visitor):
        return visitor.visitContinueStatement(self)


class BreakStatement:
    def __init__(self, token):
        self.token = token
        self.name = f"<break>"

    def linkVisitor(self, visitor):
        return visitor.visitBreakStatement(self)


class WhileStatement:
    def __init__(self, expression, block_statement, end_block_statement=None):
        self.expression = expression
        self.block_statement = block_statement
        self.end_block_statement = end_block_statement
        self.name = f"<while>"

    def linkVisitor(self, visitor):
        return visitor.visitWhileStatement(self)


class IfStatement:
    def __init__(self, expression, if_block_statement, else_block_statement=None):
        self.expression = expression
        self.if_block_statement = if_block_statement
        self.else_block_statement = else_block_statement

        self.name1 = f"<if>"
        self.name2 = f"<else>"

    def linkVisitor(self, visitor):
        return visitor.visitIfStatement(self)


class BlockStatement:
    def __init__(self, statements):
        self.statements = statements
        self.name = f"<Block>"

    def linkVisitor(self, visitor):
        return visitor.visitBlockStatement(self)


class AssignmentStatement:
    # lvalue : simple identifier token. (todo, make lvalue an expression)
    # rvalue : expression
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.name = f"<Assignment>"

    def linkVisitor(self, visitor):
        return visitor.visitAssignmentStatement(self)


class ReassignmentStatement:
    # lvalue : assignable variable
    # rvalue : expression
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.name = f"<Reassignment>"

    def linkVisitor(self, visitor):
        return visitor.visitReassignmentStatement(self)


class PrintStatement:
    def __init__(self, expr):
        self.expr = expr
        self.name = f"<{TokenType.PRINT.value}>"

    def linkVisitor(self, visitor):
        return visitor.visitPrintStatement(self)


class ExpressionStatement:
    def __init__(self, expr):
        self.expr = expr
        self.name = f"<Expression>"

    def linkVisitor(self, visitor):
        return visitor.visitExpressionStatement(self)


class BinaryExpression:
    # here [left, right] -> _Expresssion
    # operator -> Token class defined in lexer.py which has 4 properties: token_type, lexeme, literal, value
    def __init__(self, left, operator, right):
        self.left = left
        self.right = right
        self.operator = operator

    def linkVisitor(self, visitor):
        return visitor.visitBinaryExpression(self)

    # def print(self):
    #   return f'({self.operator.lexeme} {self.left.print()} {self.right.print()})'

    # def print(self):
    #   return f'({self.operator.lexeme} {self.right.print()})'


class FunctionExpression:
    def __init__(self, caller_expr, args):
        self.caller_expr = caller_expr
        self.args = args

    def linkVisitor(self, visitor):
        return visitor.visitCallableExpression(self)


class GroupingExpression:
    def __init__(self, expression):
        self.expression = expression

    def linkVisitor(self, visitor):
        return visitor.visitGroupingExpression(self)

    # def print(self):
    #   return f'({self.expression.print()})'


class GetExpression:
    # obj: LiteralExpression, prop_or_method: Token
    def __init__(self, expr, prop_or_method):
        self.expr = expr
        self.prop_or_method = prop_or_method

    def linkVisitor(self, visitor):
        return visitor.visitGetExpression(self)


################################################################################################
class LiteralExpression:
    def __init__(self, expr):
        self.expr = expr
        self.value = expr.literal  # this is just for number, string only

    def linkVisitor(self, visitor):
        return visitor.visitLiteralExpression(self)


class UnaryExpression:
    def __init__(self, operator, right):
        self.right = right
        self.operator = operator

    def linkVisitor(self, visitor):
        return visitor.visitUnaryExpression(self)


from lexer import TokenType, Scanner, Token


class Parser:
    def __init__(self, token_list):
        self.token_list = token_list
        self.current = 0
        self.interpreter = None
        self.AST = []  # list of statements

    def parse(self):
        self.AST = self.parseProgram()

    def parseProgram(self):  # returns list statements
        AST = []
        self.setCurrentAST(AST)
        while self.peek().tipe != TokenType.EOF:
            # this is executed every loop so as to prevent indirection to other intermediate AST list
            statement = self.parseStatement()
            # print('statement  -> ', statement)

            if statement is not None:
                # print('append')
                # print(f"{self.peek().tipe}")
                AST.append(statement)

            if self.peek().tipe == TokenType.SEMICOLON:
                self.advance()  # consume the semicolon
                # print('semicolon consumed')
            else:
                raise Exception(
                    f"statement is not terminated by semicolon at line {self.peek().line}"
                )
        return AST

    def parseStatement(self):
        # variable statement
        # print statement
        # expression statement, reassignment statement
        # block statement
        # if statement

        if variable_statement := self.variableStatement():
            return variable_statement

        # important if you're looking for anon function
        if block_statement := self.blockStatement():
            return block_statement

        if if_statement := self.ifStatement():
            return if_statement
        # match is syntactic sugar
        if match_statement := self.matchStatement():
            # print('match_statement')
            return match_statement

        if print_statement := self.printStatement():
            return print_statement

        if while_statement := self.whileStatement():
            return while_statement

        # for is syntactic sugar
        if for_statement := self.forStatement():
            return for_statement

        if return_statement := self.returnStatement():
            return return_statement

        if function_statement := self.functionStatement():
            return function_statement

        if class_statement := self.classStatement():
            return class_statement

        if continue_statement := self.continueStatement():
            return continue_statement

        if break_statement := self.breakStatement():
            return break_statement

        # here order is important, expression statement must come at last
        # expressiontStatement returns ReassignmentStatement as well as Expression statement, it is due to the way the parsing is performed
        # instance checking needs to be done only in the following and not the above because all above statement depends upon the following
        # and checking null in the following is sufficient to generate error free code
        if expression_statement := self.expressionStatement():
            if (
                isinstance(expression_statement, ReassignmentStatement)
                and expression_statement.lvalue is not None
            ):
                return expression_statement
            if (
                isinstance(expression_statement, ExpressionStatement)
                and expression_statement.expr is not None
            ):
                return expression_statement

    def continueStatement(self):
        if self.peek().tipe == TokenType.CONTINUE:
            token = self.advance()
            return ContinueStatement(token=token)

    def breakStatement(self):
        if self.peek().tipe == TokenType.BREAK:
            token = self.advance()
            return BreakStatement(token=token)

    def classStatement(self):
        # print('in class statement')
        if self.peek().tipe == TokenType.CLASS:
            class_token = self.advance()  # consume class
            # print('token ', class_token.toString())
            class_identifier_token = self.advance()
            # print('ident ', class_identifier_token.toString())
            left_brace = (
                self.advance()
            )  # replace this with expect function to check whether there is left paren or not
            # print('left paren ', left_brace.toString())
            function_statements = []  # store the function definition
            variable_statements = []
            while self.peek().tipe != TokenType.RIGHT_BRACE:
                # print('right paren searching')
                if self.peek().tipe == TokenType.EOF:
                    raise Exception(
                        f"parenthesis is not terminated by matching parenthesis at line # {left_paren.line}"
                    )

                if function_statement := self.functionStatement():
                    if self.peek().tipe == TokenType.SEMICOLON:
                        function_statements.append(function_statement)
                        self.advance()  # consume the semicolon
                    else:
                        raise Exception(
                            f"->statement not terminated at line {self.peek().line}"
                        )
                elif variable_statement := self.variableStatement():
                    if self.peek().tipe == TokenType.SEMICOLON:
                        variable_statements.append(variable_statement)
                        self.advance()  # consume the semicolon
                    else:
                        raise Exception(
                            f"->statement not terminated at line {self.peek().line}"
                        )
                else:
                    raise Exception(f"non allowed statement at line {self.peek().line}")

            self.advance()  # consume the right brace

            return ClassStatement(
                LiteralExpression(class_identifier_token),
                function_statements,
                variable_statements,
            )

    def functionStatement(self):
        # the following conditional checks if it's normal function statement or anon function expression
        # if identifier is provided after `fun` its function statement
        if self.peek().tipe == TokenType.FUN:
            function_token = self.advance()  # consume the fun token
            function_identifier_expression = LiteralExpression(self.advance())
            left_paren = self.advance()
            params_list = []
            if (
                self.peek().tipe == TokenType.IDENTIFIER
            ):  # handles case of zero argument
                arg = self.advance()
                params_list.append(LiteralExpression(arg))

            while self.peek().tipe != TokenType.RIGHT_PAREN:
                if self.peek().tipe == TokenType.EOF:
                    raise Exception(
                        f"parenthesis is not terminated by matching parenthesis at line # {left_paren.line}"
                    )

                if self.peek().tipe == TokenType.COMMA:
                    self.advance()  # consume comma
                    if self.peek().tipe == TokenType.IDENTIFIER:
                        arg = self.advance()
                        params_list.append(LiteralExpression(arg))
                    else:
                        raise Exception("function parameter must be identifier")
                else:
                    raise Exception(
                        f"function argument must be separated by comma at line # {self.peek().line}"
                    )

            self.advance()  # consume right paren

            block_statement = self.blockStatement()

            return FunctionStatement(
                function_identifier_expression, params_list, block_statement
            )

    def variableStatement(self):
        # variable statement
        # print(self.peek().tipe, TokenType.VAR)
        if self.peek().tipe == TokenType.VAR:
            # print("consumed var keyword")
            self.advance()  # consume the var keyword
            # var must be initialized with value mandatorily
            # print("after var ", self.peek().tipe, " gone lvalue parsing")
            lvalue = self.parseExpr()  # self.advance()
            # print(f"variableStatement -> {ASTPrinter().print(lvalue)}")
            if self.peek().tipe == TokenType.EQUAL:
                self.advance()  # consume the equal sign
                rvalue = self.parseExpr()
                # print(f'variableStatement -> {ASTPrinter().print(rvalue)}')
                assignment_statement = AssignmentStatement(lvalue, rvalue)
                return assignment_statement
            else:
                raise Exception(
                    "var keyword must be followed by identifier, equals sign and a mandatory rvalue"
                )

    def returnStatement(self):
        if self.peek().tipe == TokenType.RETURN:
            return_keyword = self.advance()
            try:
                ret_expr = self.parseExpr()
                return ReturnStatement(ret_expr)
            except:
                return ReturnStatement(expr=None)

    def blockStatement(self):
        # anon function requiremnt, whenever you enter a block get a reference to parent AST and at the end
        # setthe current AST to this parent ast

        parent_ast = self.getCurrentAST()
        # block statement
        if self.peek().tipe == TokenType.LEFT_BRACE:
            left_brace = self.advance()  # consume the left brace
            statements = []

            self.setCurrentAST(statements)  # useful for anon function

            while self.peek().tipe != TokenType.RIGHT_BRACE:
                if self.peek().tipe == TokenType.EOF:
                    raise Exception(
                        f"Block statement not terminated by matching brace at line {left_brace.line}"
                    )

                statement = self.parseStatement()
                # look for ; in the next token
                if self.peek().tipe == TokenType.SEMICOLON:
                    self.advance()  # consumet the semicolon
                    statements.append(statement)
                else:
                    raise Exception(
                        f"->statement not terminated at line {self.peek().line}"
                    )

            self.advance()  # consume the right brace
            # setting current AST to be the parent ast
            self.setCurrentAST(parent_ast)
            return BlockStatement(statements)

    def printStatement(self):
        # print statement
        if self.peek().tipe == TokenType.PRINT:
            p_statement = (
                self.advance()
            )  # not actually required, we can discard this value
            expr = self.parseExpr()
            # print('expr ', expr, expr.value)
            return PrintStatement(expr)
        # the following handles expression statement as well as reassignment statement

    def expressionStatement(self):
        lvalue = self.parseExpr()
        if self.peek().tipe in [
            TokenType.EQUAL,
            TokenType.MINUS_EQUAL,
            TokenType.PLUS_EQUAL,
            TokenType.STAR_EQUAL,
            TokenType.SLASH_EQUAL,
        ]:  # this is reassignment statement
            # the or operator is there to check for obj.propery reassignment expression
            # if (lvalue.expr.tipe == TokenType.IDENTIFIER ): #check if the lvalue is assignable variable
            operator = self.advance()  # consume the sign =, -=, +=, *=, /=
            rvalue = self.parseExpr()
            if operator.tipe == TokenType.EQUAL:
                return ReassignmentStatement(lvalue, rvalue)
            ### (syntactic sugar)the following procedure replaces the double token with their equivalent single token operator and at the
            ### end carry out syntactic operation of binaryExpression and return it as
            if operator.tipe == TokenType.PLUS_EQUAL:
                operator.tipe = TokenType.PLUS

            if operator.tipe == TokenType.MINUS_EQUAL:
                operator.tipe = TokenType.MINUS

            if operator.tipe == TokenType.STAR_EQUAL:
                operator.tipe = TokenType.STAR

            if operator.tipe == TokenType.SLASH_EQUAL:
                operator.tipe = TokenType.SLASH

            syntactic_expression = BinaryExpression(lvalue, operator, rvalue)
            return ReassignmentStatement(lvalue, syntactic_expression)
            # else:
            #     raise Exception("non assignable target")
        else:  # if there is no equlity sign then it must be expression statement
            return ExpressionStatement(lvalue)

    def matchStatement(self):
        allowed_logical_operator_token = [
            TokenType.EQUAL_EQUAL,
            TokenType.BANG_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ]

        if self.peek().tipe == TokenType.MATCH:
            self.advance()  # advance the match keyword

            match_expr = self.parseExpr()

            # the following expression is mandatory, however since the parseExpr() function now raises execption on none value, the following check might not be required
            # if (match_expr is None):
            #     raise Exception(f"match statement must be followed by valid expresion at line {self.peek().line}")

            if self.peek().tipe != TokenType.LEFT_BRACE:
                raise Exception(
                    f"match statemetn must start with {{{ {} }}} at line {self.peek().line}"
                )

            self.advance()  # advance the {

            #########################################################################################################
            # first case statement
            if self.peek().tipe != TokenType.CASE:
                raise Exception(
                    f"match statement must contain matching case statement at line {self.peek().line}"
                )

            self.advance()  # advance the case keyword

            ################################################################# operator before case
            if self.peek().tipe in allowed_logical_operator_token:
                operator = self.advance()
            else:  # if not default is ==
                operator = Token(
                    tipe=TokenType.EQUAL_EQUAL,
                    lexeme="==",
                    literal="",
                    line=self.peek().line,
                )

            #################################################################

            case = self.parseExpr()

            ####this check might not be required
            # if (case is None):
            #     raise Exception(f"case statement must be followed by valid expresion at line {self.peek().line}")

            if self.peek().tipe != TokenType.FAT_ARROW:
                raise Exception(
                    f"missing associated => in case statement at line {self.peek().line}"
                )

            self.advance()  # advance the => token

            if_block_statement = self.parseStatement()

            if_statement = IfStatement(
                expression=BinaryExpression(
                    left=match_expr, operator=operator, right=case
                ),
                if_block_statement=if_block_statement,
                else_block_statement=None,
            )  # we currently don't have matching else block, we will fill it up later

            # add the reference of original if statement so that it can be returned, the above if_statement is continually mutated in the following
            # loop to allow chained if_statement
            return_if_statement = if_statement

            ########################################################################################################

            ####################################################################################
            # other case statements
            is_default = False  # notify when default statement is parsed
            while True:
                if self.peek().tipe == TokenType.RIGHT_BRACE:
                    self.advance()  # consume right brace, end of statement
                    break

                if self.peek().tipe != TokenType.CASE:
                    raise Exception(
                        f"match statement must contain matching case statement at line {self.peek().line}"
                    )

                self.advance()  # advance the case keyword

                # check for default keyword after case keyword
                if self.peek().tipe == TokenType.DEFAULT:
                    if (
                        is_default
                    ):  # if is_default == true, we have already parsed default case and two default is error
                        raise Exception(
                            f"Multiple default case found at line {self.peek().line}"
                        )
                    else:
                        self.advance()  # consume default keyword
                        is_default = True
                else:
                    # if default is not found check for logical comparison operator as ususal
                    ################################################################# operator before expression
                    if self.peek().tipe in allowed_logical_operator_token:
                        operator = self.advance()
                    else:  # if not default is ==
                        operator = Token(
                            tipe=TokenType.EQUAL_EQUAL,
                            lexeme="==",
                            literal="",
                            line=self.peek().line,
                        )

                    #################################################################
                    case = self.parseExpr()
                    # print('case ', ASTPrinter().print(case), case.right)

                    # this might not be required
                    # if (case is None):
                    #    raise Exception(f"case statement must be followed by valid expresion at line {self.peek().line}")

                if self.peek().tipe != TokenType.FAT_ARROW:
                    raise Exception(
                        f"missing associated => in case statement at line {self.peek().line}"
                    )

                self.advance()  # advance the => token

                else_block_statement = self.parseStatement()

                # if default is parsed, it is immediately the final else statement
                if is_default:
                    if_statement.else_block_statement = else_block_statement

                else:  # for regualar statements
                    else_statement = IfStatement(
                        expression=BinaryExpression(
                            left=match_expr, operator=operator, right=case
                        ),
                        if_block_statement=else_block_statement,
                        else_block_statement=None,
                    )  # we currently don't have matching else block, we will fill it up later

                    if_statement.else_block_statement = else_statement

                    if_statement = else_statement

            ####################################################################################
            return return_if_statement

    def ifStatement(self):
        if self.peek().tipe == TokenType.IF:
            self.advance()  # advance the 'if' token
            expression = self.parseExpr()
            if if_block_statement := self.blockStatement():
                if self.peek().tipe == TokenType.ELSE:
                    self.advance()  # consume the 'else' token
                    if else_block_statement := self.blockStatement():
                        return IfStatement(
                            expression, if_block_statement, else_block_statement
                        )
                    else:
                        raise Exception(
                            f"else statement must be followed by matching braces at line {self.peek().line}"
                        )
                else:
                    return IfStatement(expression, if_block_statement)
            else:
                raise Exception(
                    f"if statement must be followed by matching braces at line {self.peek().line}"
                )

    def forStatement(self):
        # this whole is a syntactic sugar for whilestatement
        if self.peek().tipe == TokenType.FOR:
            self.advance()  # consume for keyword

            if self.peek().tipe != TokenType.LEFT_PAREN:
                raise Exception(
                    f"for statement should be followed by parenthesis in at line {self.peek().line}"
                )

            self.advance()  # consume the `(`

            try:
                initializer_statement = self.parseStatement()
            except:
                initializer_statement = (
                    None  # if initializer is not found, leave it, it's optional
                )

            if self.peek().tipe != TokenType.SEMICOLON:
                raise Exception(
                    f"for statement parameters must be separated by semicolon at line {self.peek().line}"
                )
            self.advance()  # consume the semicolon

            condition = self.parseExpr()
            if condition is None:
                raise Exception(
                    f"for statement needs to have compulsory condition check at line {self.peek().line}"
                )

            if self.peek().tipe != TokenType.SEMICOLON:
                raise Exception(
                    f"for statement parameters must be separated by semicolon at line {self.peek().line}"
                )
            self.advance()  # consume the semicolon

            try:
                increment_statement = (
                    self.parseStatement()
                )  # optional so doesn't raised exception
            except:
                increment_statement = None
                # it's optional

            if self.peek().tipe != TokenType.RIGHT_PAREN:
                raise Exception(
                    f"no matching parenthesis in for statement at line {self.peek().line}"
                )
            self.advance()  # consume the right paren

            block_statement = self.blockStatement()
            # if increment_statement is not None:
            # block_statement.statements.append(increment_statement) # direct AST manipulation must be explicitly checked for None type

            while_statement = WhileStatement(
                condition, block_statement, increment_statement
            )

            # add the initializer_statement before the body of the while statement, at the top
            if (
                initializer_statement is not None
            ):  # direct AST manipulation must be explicitly checked for None type
                self.getCurrentAST().append(initializer_statement)

            return while_statement

    #         else:
    #             raise Exception(f"no matching parenthesis in for statement at line {self.peek().line}")
    #     else:
    #         raise Exception(f"for statement parameters must be separated by semicolon at line {self.peek().line}")
    # else:
    #     raise Exception(f"for statement parameters must be separated by semicolon at line {self.peek().line}")

    #     raise Exception(f"for statement should be followed by parenthesis in at line {self.peek().line}")

    def whileStatement(self):
        if self.peek().tipe == TokenType.WHILE:
            self.advance()  # consume the `while` token
            expression = self.parseExpr()
            if block_statement := self.blockStatement():
                return WhileStatement(expression, block_statement)
            else:
                raise Exception(
                    f"while statement must be followed by matching braces at line {self.peek().line}"
                )

    def parseExpr(self):
        return self.logicalExpr()

    def logicalExpr(self):
        expr = self.comparisonExpr()

        while self.peek().tipe in [TokenType.AND, TokenType.OR]:
            operator = self.advance()  # return `and` or `or`
            right_expr = self.comparisonExpr()
            expr = BinaryExpression(expr, operator, right_expr)

        return expr

    def comparisonExpr(self):
        expr = self.additionExpr()

        while self.peek().tipe in [
            TokenType.EQUAL_EQUAL,
            TokenType.BANG_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ]:
            operator = self.advance()  # consume the operator and move forward
            right_expr = self.additionExpr()
            expr = BinaryExpression(expr, operator, right_expr)

        return expr

    def additionExpr(self):
        expr = self.multiplicationExpr()

        while self.peek().tipe in [TokenType.PLUS, TokenType.MINUS]:
            operator = self.advance()
            right_expr = self.multiplicationExpr()
            expr = BinaryExpression(expr, operator, right_expr)

        return expr

    def multiplicationExpr(self):
        expr = self.unitaryExpr()
        while self.peek().tipe in [TokenType.STAR, TokenType.SLASH, TokenType.MODULO]:
            operator = self.advance()  # consume the operator
            right_expr = self.unitaryExpr()
            expr = BinaryExpression(expr, operator, right_expr)

        return expr

    def unitaryExpr(self):
        if self.peek().tipe in [TokenType.BANG, TokenType.MINUS, TokenType.PLUS]:
            operator = self.advance()  # advance the operator
            return UnaryExpression(operator, self.unitaryExpr())

        return self.callerExpr()

    # this function calculates function and object.methods and objects.properties
    def callerExpr(self):
        #################################
        def argument_list():
            args = []
            # if (arg:= self.parseExpr()):
            #     args.append(arg)
            try:
                expr = self.parseExpr()
                args.append(expr)
            except:
                pass

            while self.peek().tipe != TokenType.RIGHT_PAREN:
                # breakpoint()
                if self.peek().tipe == TokenType.EOF:
                    raise Exception(
                        f"no matching parenthesis at line {left_paren.line}"
                    )
                elif self.peek().tipe == TokenType.COMMA:
                    # print('comman')
                    self.advance()  # consume the comma
                    arg = self.parseExpr()
                    args.append(arg)
                else:
                    raise Exception(f"non valid syntax at {self.peek().line}")

            self.advance()  # consume the right parenthesis
            return args

        ##################################
        caller_expr = self.literalExpr()
        while True:
            # print("true")
            if self.peek().tipe == TokenType.LEFT_PAREN:
                # print('paren')
                left_paren = self.advance()
                args = argument_list()
                caller_expr = FunctionExpression(caller_expr, args)
            # new code for dot operator
            elif self.peek().tipe == TokenType.DOT:
                # print('dot')
                dot = self.advance()
                token_prop_or_method = self.advance()
                caller_expr = GetExpression(
                    caller_expr, prop_or_method=token_prop_or_method
                )
            else:
                break

        return caller_expr

    ############the folllowing function is defined in order to facilitate AST manipulation for anon function
    def getCurrentAST(self):
        return self.current_AST

    def setCurrentAST(self, current_AST):
        self.current_AST = current_AST

    ######################################################

    def literalExpr(
        self,
    ):  # this needs to add support for bracketed expr or(group expression) as they have the same precedence as the literal number
        # print('inside_literal_expr')
        if anon_function := self.anonFunctionExpr():
            return anon_function

        if self.peek().tipe in [
            TokenType.STRING,
            TokenType.NUMBER,
            TokenType.IDENTIFIER,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.THIS,
            TokenType.NIL,
        ]:
            # print('inside_literal_expr string number ... cont')
            literal_expr = self.advance()
            # print('literalExpr ', literal_expr.literal)
            return LiteralExpression(literal_expr)
        if self.peek().tipe == TokenType.LEFT_PAREN:
            # print('inside_literal_expr paren')
            self.advance()  # consume the '(' token
            group_expr = self.parseExpr()
            if self.peek().tipe == TokenType.RIGHT_PAREN:
                self.advance()  # consume the ')' token
                return group_expr
            else:
                raise Exception(
                    f"error no matching parenthesis found at {self.peek().line}"
                )  # exception needs to be raised here

        # breakpoint()

        raise Exception(f"invalid expression found at {self.peek().line} ")

    def anonFunctionExpr(self):  # anon function declaration expression
        # To do: needs to check user program for error in the following code
        if self.peek().tipe == TokenType.WALL:
            function_token = self.advance()  # consume the wall token
            # this is an anonymous function declaration
            function_identifier_token = Token(
                TokenType.IDENTIFIER, lexeme="", literal="", line=function_token.line
            )
            function_identifier_token.literal = f"@{hash(function_identifier_token)}"  # generate unique id for anonyous function
            function_identifier_expression = LiteralExpression(
                function_identifier_token
            )

            params_list = []
            if (
                self.peek().tipe == TokenType.IDENTIFIER
            ):  # handles case of zero argument
                arg = self.advance()
                params_list.append(LiteralExpression(arg))

            while self.peek().tipe != TokenType.WALL:
                if self.peek().tipe == TokenType.EOF:
                    raise Exception(
                        f"parenthesis is not terminated by matching parenthesis at line # {left_paren.line}"
                    )

                if self.peek().tipe == TokenType.COMMA:
                    self.advance()  # consume comma
                    if self.peek().tipe == TokenType.IDENTIFIER:
                        arg = self.advance()
                        params_list.append(LiteralExpression(arg))
                    else:
                        raise Exception("function parameter must be identifier")
                else:
                    raise Exception(
                        f"function argument must be separated by comma at line # {self.peek().line}"
                    )

            self.advance()  # consume right paren

            block_statement = self.blockStatement()

            # self.AST.append(FunctionStatement(function_identifier_token, params_list, block_statement))
            # side effect
            function_statement = FunctionStatement(
                function_identifier_expression, params_list, block_statement
            )

            self.getCurrentAST().append(function_statement)
            # end side effect

            return function_identifier_expression

    def advance(self):
        self.current += 1
        return self.token_list[self.current - 1]

    def reverse(self):
        return self.token_list[self.current - 1]

    def peek(self):
        return self.token_list[self.current] if not self.isAtEnd() else TokenType.EOF

    def peekNext(self):
        return (
            self.token_list[self.current + 1]
            if not self.isAtEndWhere(n=self.current + 1)
            else TokenType.EOF
        )

    def peekAndMatch(self, match_token):
        if self.peek() == match_with_token:
            self.advance()
            return True
        return False

    def peekAndMatchMultiple(self, *match_tokens):
        return any(map(self.peekAndMatch, match_tokens))

    def isAtEnd(self):
        return self.current >= len(self.token_list)  # check the type of the end item

    # temporary helper functoin to facilitate peekNext() function
    def isAtEndWhere(self, n):
        return n >= len(self.token_list)
