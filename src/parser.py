class ClassStatement():
    def __init__(self, class_identifier_expression, function_statements, variable_statements):
        self.class_identifier_expression = class_identifier_expression
        self.function_statements = function_statements
        self.variable_statements = variable_statements

        ##check if class constructor is defined, raise error if not 

        class_name_token = self.class_identifier_expression.expr
        if class_name_token.literal not in map(lambda function: function.function_identifier_expression.expr.literal, function_statements):
            raise Exception(f"class constructor is not defined for class {class_name_token.literal} at line {class_name_token.line}")
        #to do: check if the class constructor have return statement and raise error if it's present 

        self.name = "<class>"

    def linkVisitor(self, visitor):
        return visitor.visitClassStatement(self)


########################################################
class FunctionStatement:
    def __init__(self, function_identifier_expression, params_list, block_statement):
        self.function_identifier_expression = function_identifier_expression
        self.params_list = params_list #list of token
        self.block_statement = block_statement #BlockStatement

        self.name = "<function>"

    def linkVisitor(self, visitor):
        return visitor.visitFunctionStatement(self)

class ReturnStatement:
    def __init__(self, expr):
        self.expr = expr
        self.name = f"<return>"

    def linkVisitor(self, visitor):
        return visitor.visitReturnStatement(self)

class WhileStatement:
    def __init__(self, expression, block_statement):
        self.expression = expression
        self.block_statement = block_statement
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
    #lvalue : simple identifier token. (todo, make lvalue an expression)
    #rvalue : expression
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue 
        self.name = f"<Assignment>"

    def linkVisitor(self, visitor):
        return visitor.visitAssignmentStatement(self)

class ReassignmentStatement:
    #lvalue : assignable variable
    #rvalue : expression
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
    #here [left, right] -> _Expresssion
    #operator -> Token class defined in lexer.py which has 4 properties: token_type, lexeme, literal, value
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
    #obj: LiteralExpression, prop_or_method: Token
    def __init__(self, expr, prop_or_method):
        self.expr = expr
        self.prop_or_method = prop_or_method

    def linkVisitor(self, visitor):
        return visitor.visitGetExpression(self)
################################################################################################
class LiteralExpression:
    def __init__(self, expr):
        self.expr = expr
        self.value = expr.literal #this is just for number, string only 

    def linkVisitor(self, visitor):
        return visitor.visitLiteralExpression(self)

class UnaryExpression:
    def __init__(self, operator, right):
        self.right =right
        self.operator = operator

    def linkVisitor(self, visitor):
        return visitor.visitUnaryExpression(self)


from lexer import TokenType, Scanner, Token
class Parser:
    def __init__(self, token_list):
        self.token_list = token_list
        self.current = 0
        self.interpreter = None
        self.AST = [] # list of statements 

    def parse(self):
        self.AST = self.parseProgram()

    def parseProgram(self): #returns list statements
        AST = []
        self.setCurrentAST(AST)
        while (self.peek().tipe != TokenType.EOF):
            #this is executed every loop so as to prevent indirection to other intermediate AST list 
            statement = self.parseStatement()
            # print('statement  -> ', statement)
            if (self.peek().tipe == TokenType.SEMICOLON):
                self.advance()#consume the semicolon
                AST.append(statement)
            else:
                raise Exception(f'statement is not terminated by semicolon at line {self.peek().line}')
        return AST 

    def parseStatement(self):
        #variable statement
        #print statement 
        #expression statement, reassignment statement
        #block statement
        #if statement

        if (variable_statement := self.variableStatement()):
            return variable_statement

        # important if you're looking for anon function 
        if (block_statement := self.blockStatement()):
            return block_statement

        if (if_statement := self.ifStatement()):
            return if_statement

        if (print_statement := self.printStatement()):
            return print_statement

        if (while_statement := self.whileStatement()):
            return while_statement

        if(return_statement := self.returnStatement()):
            return return_statement

        if (function_statement := self.functionStatement()):
            return function_statement

        if (class_statement := self.classStatement()):
            return class_statement
        #here order is important, expression statement must come at last 
        if (expression_statement := self.expressionStatement()):
            return expression_statement
            

    def classStatement(self):
        # print('in class statement')
        if (self.peek().tipe == TokenType.CLASS):
            class_token = self.advance() # consume class
            # print('token ', class_token.toString())
            class_identifier_token = self.advance()
            # print('ident ', class_identifier_token.toString())
            left_brace = self.advance() # replace this with expect function to check whether there is left paren or not
            # print('left paren ', left_brace.toString())
            function_statements = [] #store the function definition
            variable_statements = []
            while(self.peek().tipe != TokenType.RIGHT_BRACE):
                # print('right paren searching')
                if (self.peek().tipe == TokenType.EOF):
                    raise Exception(f"parenthesis is not terminated by matching parenthesis at line # {left_paren.line}")

                if (function_statement:= self.functionStatement()):
                    if (self.peek().tipe == TokenType.SEMICOLON):
                        function_statements.append(function_statement)
                        self.advance() # consume the semicolon
                    else:
                        raise Exception(f'->statement not terminated at line {self.peek().line}')
                elif (variable_statement := self.variableStatement()):
                    if (self.peek().tipe == TokenType.SEMICOLON):
                        variable_statements.append(variable_statement)
                        self.advance() # consume the semicolon
                    else:
                        raise Exception(f'->statement not terminated at line {self.peek().line}')
                else:
                    raise Exception(f"non allowed statement at line {self.peek().line}")

            self.advance() # consume the right brace

            return ClassStatement(LiteralExpression(class_identifier_token), function_statements, variable_statements)


                
    def functionStatement(self):
        #the following conditional checks if it's normal function statement or anon function expression
        #if identifier is provided after `fun` its function statement 
        if(self.peek().tipe == TokenType.FUN):
            function_token = self.advance() # consume the fun token 
            function_identifier_expression = LiteralExpression(self.advance())
            left_paren = self.advance()
            params_list = []
            if (self.peek().tipe == TokenType.IDENTIFIER): #handles case of zero argument
                arg = self.advance()
                params_list.append(LiteralExpression(arg))

            while(self.peek().tipe != TokenType.RIGHT_PAREN):
                if (self.peek().tipe == TokenType.EOF):
                    raise Exception(f"parenthesis is not terminated by matching parenthesis at line # {left_paren.line}")
                
                if(self.peek().tipe == TokenType.COMMA):
                    self.advance() # consume comma
                    if (self.peek().tipe == TokenType.IDENTIFIER):
                        arg = self.advance()
                        params_list.append(LiteralExpression(arg))
                    else:
                        raise Exception('function parameter must be identifier')
                else:
                    raise Exception(f"function argument must be separated by comma at line # {self.peek().line}")

            self.advance()# consume right paren

            block_statement = self.blockStatement()

            return FunctionStatement(function_identifier_expression, params_list, block_statement)


    def variableStatement(self):
        #variable statement
        if (self.peek().tipe == TokenType.VAR):
            self.advance() # consume the var keyword
            #var must be initialized with value mandatorily
            lvalue = self.parseExpr() #self.advance()
            # print(f'variableStatement -> {ASTPrinter().print(lvalue)}')
            if (self.peek().tipe == TokenType.EQUAL):
                self.advance() # consume the equal sign
                rvalue = self.parseExpr()
                # print(f'variableStatement -> {ASTPrinter().print(rvalue)}')
                assignment_statement = AssignmentStatement(lvalue, rvalue)
                return assignment_statement
            else:
                raise Exception('var keyword must be followed by identifier, equals sign and a mandatory rvalue')

    def returnStatement(self):
        if (self.peek().tipe == TokenType.RETURN):
            return_keyword = self.advance()
            if (ret_expr := self.parseExpr()):
                return ReturnStatement(ret_expr)

    def blockStatement(self):
        #anon function requiremnt, whenever you enter a block get a reference to parent AST and at the end 
        #setthe current AST to this parent ast

        parent_ast = self.getCurrentAST()
        #block statement
        if(self.peek().tipe == TokenType.LEFT_BRACE):
            left_brace = self.advance() # consume the left brace
            statements = []
            
            self.setCurrentAST(statements)#useful for anon function 

            while (self.peek().tipe != TokenType.RIGHT_BRACE):
                if (self.peek().tipe == TokenType.EOF):
                    raise Exception(f'Block statement not terminated by matching brace at line {left_brace.line}')
                
                statement = self.parseStatement()
                #look for ; in the next token
                if (self.peek().tipe == TokenType.SEMICOLON):
                    self.advance() # consumet the semicolon
                    statements.append(statement)
                else:
                    raise Exception(f'->statement not terminated at line {self.peek().line}')

            self.advance() # consume the right brace
            #setting current AST to be the parent ast  
            self.setCurrentAST(parent_ast)
            return BlockStatement(statements)

    def printStatement(self):
        # print statement
        if (self.peek().tipe == TokenType.PRINT): 
            p_statement = self.advance()#not actually required, we can discard this value
            expr = self.parseExpr()
            # print('expr ', expr, expr.value)
            return PrintStatement(expr)
        # the following handles expression statement as well as reassignment statement

    def expressionStatement(self):
        lvalue = self.parseExpr()
        if (self.peek().tipe in [TokenType.EQUAL, TokenType.MINUS_EQUAL, TokenType.PLUS_EQUAL, TokenType.STAR_EQUAL, TokenType.SLASH_EQUAL]): # this is reassignment statement
        #the or operator is there to check for obj.propery reassignment expression
            #if (lvalue.expr.tipe == TokenType.IDENTIFIER ): #check if the lvalue is assignable variable
            operator = self.advance() # consume the sign
            rvalue = self.parseExpr()
            if (operator.tipe == TokenType.EQUAL):
                return ReassignmentStatement(lvalue, rvalue)
            ### (syntactic sugar)the following procedure replaces the double token with their equivalent single token operator and at the 
            ### end carry out syntactic operation of binaryExpression and return it as
            if (operator.tipe == TokenType.PLUS_EQUAL):
                operator.tipe = TokenType.PLUS 

            if (operator.tipe == TokenType.MINUS_EQUAL):
                operator.tipe = TokenType.MINUS 

            if (operator.tipe == TokenType.STAR_EQUAL):
                operator.tipe = TokenType.STAR

            if (operator.tipe == TokenType.SLASH_EQUAL):
                operator.tipe = TokenType.SLASH

            syntactic_expression  = BinaryExpression(lvalue, operator, rvalue)
            return ReassignmentStatement(lvalue, syntactic_expression)
            # else:
            #     raise Exception("non assignable target")
        else: #if there is no equlity sign then it must be expression statement 
            return ExpressionStatement(lvalue)

    def ifStatement(self):
        if (self.peek().tipe == TokenType.IF):
            self.advance() #consume the 'if' token
            expression = self.parseExpr()
            if (if_block_statement := self.blockStatement()):
                if (self.peek().tipe == TokenType.ELSE):
                    self.advance() # consume the 'else' token
                    if else_block_statement := self.blockStatement():
                        return IfStatement(expression, if_block_statement, else_block_statement)
                    else:
                        raise Exception(f"else statement must be followed by matching braces at line {self.peek().line}")
                else:
                    return IfStatement(expression, if_block_statement)
            else:
                raise Exception(f"if statement must be followed by matching braces at line {self.peek().line}")

    def whileStatement(self):
        if (self.peek().tipe == TokenType.WHILE):
            self.advance() # consume the `while` token
            expression = self.parseExpr()
            if (block_statement := self.blockStatement()):
                return WhileStatement(expression, block_statement)
            else:
                raise Exception(f"while statement must be followed by matching braces at line {self.peek().line}")

    def parseExpr(self):
        return self.logicalExpr()

    def logicalExpr(self):
        left_expr = self.comparisonExpr()
        if (self.peek().tipe in [TokenType.AND, TokenType.OR]):
            operator = self.advance() #return `and` or `or`
            right_expr = self.logicalExpr()
            return BinaryExpression(left_expr, operator, right_expr)
        return left_expr

    def comparisonExpr(self):
        left_expr = self.additionExpr()

        if  (self.peek().tipe in [TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL,
                                  TokenType.GREATER, TokenType.GREATER_EQUAL,
                                  TokenType.LESS, TokenType.LESS_EQUAL]):
            operator = self.advance() #consume the operator and move forward
            right_expr = self.comparisonExpr()
            return BinaryExpression(left_expr, operator, right_expr)
        return left_expr

    def additionExpr(self):
        left_expr = self.multiplicationExpr()

        if(self.peek().tipe in [TokenType.PLUS, TokenType.MINUS]):
            operator = self.advance()
            right_expr = self.additionExpr()
            return BinaryExpression(left_expr, operator, right_expr)
        
        return left_expr

        
    def multiplicationExpr(self):
        left_expr = self.unitaryExpr()
        if (self.peek().tipe in [TokenType.STAR, TokenType.SLASH]):
            operator = self.advance() #consume the operator
            right_expr = self.multiplicationExpr()
            return BinaryExpression(left_expr, operator, right_expr)
        return left_expr


    def unitaryExpr(self):
        if (self.peek().tipe in [TokenType.BANG, TokenType.MINUS, TokenType.PLUS]):
            operator = self.advance() # advance the operator
            return UnaryExpression(operator, self.literalExpr())
        
        return self.callerExpr()


    #this function calculates function and object.methods and objects.properties
    def callerExpr(self):
        #################################
        def argument_list():
            args = []
            if (arg:= self.parseExpr()):
                args.append(arg)
            while(self.peek().tipe != TokenType.RIGHT_PAREN):
                if (self.peek().tipe == TokenType.EOF):
                    raise Exception(f"no matching parenthesis at line {left_paren.line}")
                if (self.peek().tipe == TokenType.COMMA):
                    self.advance()#consume the comma
                    arg = self.parseExpr()
                    args.append(arg)
            self.advance() # consume the right parenthesis
            return args
        ##################################
        caller_expr = self.literalExpr()
        while (True): 
            if (self.peek().tipe == TokenType.LEFT_PAREN):
                left_paren = self.advance()
                args = argument_list()
                caller_expr = FunctionExpression(caller_expr, args)
            #new code for dot operator
            elif(self.peek().tipe == TokenType.DOT):
                dot = self.advance()
                token_prop_or_method = self.advance()
                caller_expr = GetExpression(caller_expr, prop_or_method=token_prop_or_method)
            else:
                break
        

        return caller_expr
    ############the folllowing function is defined in order to facilitate AST manipulation for anon function 
    def getCurrentAST(self):
        return self.current_AST

    def setCurrentAST(self, current_AST):
        self.current_AST = current_AST
    ######################################################


    def literalExpr(self): # this needs to add support for bracketed expr or(group expression) as they have the same precedence as the literal number
        # print('inside_literal_expr')
        if (anon_function  := self.anonFunctionExpr()):
            return anon_function
        if (self.peek().tipe in [TokenType.STRING, TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.TRUE, TokenType.FALSE, TokenType.THIS, TokenType.NIL]):
            # print('inside_literal_expr string number ... cont')
            literal_expr = self.advance()
            # print('literalExpr ', literal_expr.literal)
            return LiteralExpression(literal_expr)
        if (self.peek().tipe == TokenType.LEFT_PAREN):
            # print('inside_literal_expr paren')
            self.advance() # consume the '(' token
            group_expr = self.parseExpr()
            if (self.peek().tipe == TokenType.RIGHT_PAREN):
                self.advance() # consume the ')' token
                return group_expr
            else:
                raise Exception(f'error no matching parenthesis found at {self.peek().line}') #exception needs to be raised here



    def anonFunctionExpr(self): # anon function declaration expression
        # To do: needs to check user program for error in the following code 
        if(self.peek().tipe == TokenType.WALL):
            function_token = self.advance() # consume the wall token 
            #this is an anonymous function declaration
            function_identifier_token = Token(TokenType.IDENTIFIER, lexeme='', literal='', line=function_token.line)
            function_identifier_token.literal = f"@{hash(function_identifier_token)}" # generate unique id for anonyous function
            function_identifier_expression = LiteralExpression(function_identifier_token)
            
            params_list = []
            if (self.peek().tipe == TokenType.IDENTIFIER): #handles case of zero argument
                arg = self.advance()
                params_list.append(LiteralExpression(arg))

            while(self.peek().tipe != TokenType.WALL):
                if (self.peek().tipe == TokenType.EOF):
                    raise Exception(f"parenthesis is not terminated by matching parenthesis at line # {left_paren.line}")
                
                if(self.peek().tipe == TokenType.COMMA):
                    self.advance() # consume comma
                    if (self.peek().tipe == TokenType.IDENTIFIER):
                        arg = self.advance()
                        params_list.append(LiteralExpression(arg))
                    else:
                        raise Exception('function parameter must be identifier')
                else:
                    raise Exception(f"function argument must be separated by comma at line # {self.peek().line}")

            self.advance()# consume right paren

            block_statement = self.blockStatement()

            # self.AST.append(FunctionStatement(function_identifier_token, params_list, block_statement))
            #side effect
            function_statement = FunctionStatement(function_identifier_expression, params_list, block_statement)
            self.getCurrentAST().append(function_statement)
            #end side effect

            return function_identifier_expression


    def advance(self):
        self.current += 1
        return self.token_list[self.current - 1]

    def reverse(self):
        return self.token_list[self.current - 1]

    def peek(self):
        return self.token_list[self.current] if not self.isAtEnd() else TokenType.EOF

    def peekNext(self):
        return self.token_list[self.current+1] if not self.isAtEndWhere(n=self.current + 1) else TokenType.EOF


    def peekAndMatch(self, match_token):
        if (self.peek() == match_with_token):
            self.advance()
            return True
        return False

    def peekAndMatchMultiple(self, *match_tokens):
        return any(map(self.peekAndMatch, match_tokens))

    def isAtEnd(self):
        return self.current >= len(self.token_list)#check the type of the end item

    #temporary helper functoin to facilitate peekNext() function
    def isAtEndWhere(self, n):
        return n >= len(self.token_list)