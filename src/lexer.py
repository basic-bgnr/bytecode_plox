from collections import defaultdict


def test(source_code="{{(+)}}"):
    scanner = Scanner(source_code)
    scanner.scanTokens()
    print(scanner.toString())


class Scanner:
    def __init__(self, source_code):
        self.source_code = source_code
        self.token_list = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.interpreter = None  # to do add interpreter to the initialization code

    # def getTokenizedList(self):
    #   self.scanTokens()
    #   return self.token_list

    def scanTokens(self):
        while not self.isAtEnd():
            self.start = self.current

            self.scanToken()

        # just for clarity
        # below line is indicative of the end of the souce_code
        self.addToken(TokenType.EOF, "")

    def isAtEnd(self):
        return self.current >= len(self.source_code)

    def scanToken(self):
        lexeme = self.advance()

        if lexeme == TokenType.MODULO.value:
            self.addToken(TokenType.MODULO, "")

        elif lexeme == TokenType.WALL.value:
            self.addToken(TokenType.WALL, "")

        elif lexeme == TokenType.LEFT_PAREN.value:
            self.addToken(TokenType.LEFT_PAREN, "")

        elif lexeme == TokenType.RIGHT_PAREN.value:
            self.addToken(TokenType.RIGHT_PAREN, "")

        elif lexeme == TokenType.LEFT_BRACE.value:
            self.addToken(TokenType.LEFT_BRACE, "")

        elif lexeme == TokenType.RIGHT_BRACE.value:
            self.addToken(TokenType.RIGHT_BRACE, "")

        elif lexeme == TokenType.COMMA.value:
            self.addToken(TokenType.COMMA, "")

        elif lexeme == TokenType.DOT.value:
            self.addToken(TokenType.DOT, "")
        ###################################### syntactic sugar
        elif lexeme == TokenType.MINUS.value:
            self.addToken(TokenType.MINUS_EQUAL, "") if (
                self.peekAndMatch(TokenType.EQUAL.value)
            ) else self.addToken(TokenType.MINUS, "")

        elif lexeme == TokenType.PLUS.value:
            self.addToken(TokenType.PLUS_EQUAL, "") if (
                self.peekAndMatch(TokenType.EQUAL.value)
            ) else self.addToken(TokenType.PLUS, "")

        elif lexeme == TokenType.STAR.value:
            self.addToken(TokenType.STAR_EQUAL, "") if (
                self.peekAndMatch(TokenType.EQUAL.value)
            ) else self.addToken(TokenType.STAR, "")

        elif lexeme == TokenType.SLASH.value:
            self.addToken(TokenType.SLASH_EQUAL, "") if (
                self.peekAndMatch(TokenType.EQUAL.value)
            ) else self.addToken(TokenType.SLASH, "")
        #########################################################
        elif lexeme == TokenType.SEMICOLON.value:
            self.addToken(TokenType.SEMICOLON, "")

        elif lexeme == TokenType.COMMENT.value:
            # this is a comment and must be consumed till the end of line
            while True:
                if self.peek() not in [
                    TokenType.NEW_LINE.value,
                    TokenType.EOF.value,
                ]:  # check for the newline or endoffile
                    self.advance()  # consume everything in between and loop till \n or \0
                else:
                    break  # if newline or eof found in self.peek()

        elif lexeme in [
            TokenType.CARRIAGE_RETURN.value,
            TokenType.SPACE.value,
            TokenType.VERTICAL_TAB.value,
            TokenType.HORIZONTAL_TAB.value,
        ]:  # ignore any of the case of return feed, space and tab
            pass  # do nothing and let it be consumed in the next cycle of scantokens function

        elif lexeme == TokenType.NEW_LINE.value:
            self.line += 1

        # two character lexemes, here peekAndMatch consumes the current token and forward if matched
        elif lexeme == TokenType.BANG.value:
            self.addToken(TokenType.BANG_EQUAL, "") if self.peekAndMatch(
                TokenType.EQUAL.value
            ) else self.addToken(TokenType.BANG, "")

        elif lexeme == TokenType.EQUAL.value:
            if self.peekAndMatch(TokenType.EQUAL.value):
                self.addToken(TokenType.EQUAL_EQUAL, "")
            elif self.peekAndMatch(TokenType.GREATER.value):
                self.addToken(TokenType.FAT_ARROW, "")
            else:
                self.addToken(TokenType.EQUAL, "")

        elif lexeme == TokenType.LESS.value:
            self.addToken(TokenType.LESS_EQUAL, "") if self.peekAndMatch(
                TokenType.EQUAL.value
            ) else self.addToken(TokenType.LESS, "")

        elif lexeme == TokenType.GREATER.value:
            self.addToken(TokenType.GREATER_EQUAL, "") if self.peekAndMatch(
                TokenType.EQUAL.value
            ) else self.addToken(TokenType.GREATER, "")

        elif lexeme == TokenType.STRING.value:  # check if lexeme is equal to "
            accumulated_string = ""
            while True:
                next_value = self.peek()
                if next_value == TokenType.EOF.value:
                    # print('eror')
                    # todo : log error to interpreter
                    raise Exception(f"no matching string quote at line {self.line}")

                if next_value != TokenType.STRING.value:  # check for closing " value
                    if (
                        next_value == TokenType.NEW_LINE.value
                    ):  # allows multiline string but the edge condition is that we need to implicitly add line
                        accumulated_string += next_value
                        self.advance()
                        self.line += 1  #

                    elif next_value == TokenType.BACK_SLASH.value:
                        self.advance()  # consume the backSlash
                        next_value = self.peek()
                        if next_value == "n":
                            accumulated_string += TokenType.NEW_LINE.value
                            self.advance()
                        elif next_value == "r":
                            accumulated_string += TokenType.CARRIAGE_RETURN.value
                            self.advance()
                        elif next_value == "t":
                            accumulated_string += TokenType.HORIZONTAL_TAB.value
                            self.advance()
                        elif next_value == "v":
                            accumulated_string += TokenType.VERTICAL_TAB.value
                            self.advance()
                        elif next_value == "b":
                            accumulated_string += "\b"
                            self.advance()
                        elif next_value == TokenType.BACK_SLASH.value:
                            accumulated_string += TokenType.BACK_SLASH.value
                            self.advance()
                        elif next_value == TokenType.STRING.value:
                            accumulated_string += TokenType.STRING.value
                            self.advance()
                        else:
                            raise Exception(
                                f"no matching escape sequence at line {self.line}"
                            )
                    else:
                        accumulated_string += next_value
                        self.advance()

                    # start consuming the value

                    # here we don't need to keep track of what values we are consuming because we already have
                    # specified the start and current variable which we can utilize to extract the consumed string from the source code
                else:
                    string_value = accumulated_string  # the startposition is at " so + 1 and self.current is at " so no adding since substring cause n-1 string to be included
                    # print('parsed string ', string_value)
                    self.addToken(
                        TokenType.STRING, string_value
                    )  # here we have to remove the occurrence of " " so we can't rely on automatic literals
                    self.advance()  # consume the last "
                    break

        elif lexeme in TokenType.NUMBER.value:
            ####helper function ############################
            def consumeDigits():
                #####consumes continuous digit without . with optional SEPARATOR
                while (
                    self.peek() in TokenType.NUMBER.value
                    or self.peek() == TokenType.SEPARATOR.value
                ):  # the second and subsequent digit can be _
                    self.advance()  # the current number is digit so consume it

            ###########################
            def checkDecimal():
                if (
                    self.peek() == TokenType.DOT.value
                    and self.peekNext() in TokenType.NUMBER.value
                ):  # check for optional . and if present check if the next peeked value is also a number otherwise out `method` calling syntax won't work
                    self.advance()
                    return True
                return False

            #####helper function end #######################

            consumeDigits()  # before decimal
            if (
                checkDecimal()
            ):  #######consumes digits after decimal with optional SEPARATOR
                consumeDigits()

            number_value = self.source_code[self.start : self.current].replace(
                TokenType.SEPARATOR.value, ""
            )  # replace occurrence of _ with void value
            self.addToken(
                TokenType.NUMBER, float(number_value)
            )  # here we can't rely on the automatic generator since there are items to be removed

        elif (
            lexeme in TokenType.IDENTIFIER.value or lexeme == TokenType.SEPARATOR.value
        ):  # identifier can being with alphabet or _
            while (
                self.peek() in TokenType.IDENTIFIER.value
                or self.peek() in TokenType.NUMBER.value
                or self.peek() in TokenType.SEPARATOR.value
            ):  # after first(alphabet or _) the remaining number can be (alphabet _ or numbers)
                self.advance()

            reserved_keywords = defaultdict(
                lambda: None,
                {
                    keyword.value: token_keyword
                    for keyword in KeywordTokens
                    for token_keyword in TokenType
                    if token_keyword.value == keyword.value
                },
            )

            literal = self.getLiteral()
            if reserved_keyword := reserved_keywords[
                literal
            ]:  # this is unique system for python 3
                self.addToken(
                    reserved_keyword, reserved_keyword.value
                )  # we explicitly add '' since we do not want to depend upon autogenerated values
            # if non of the reserved keywords matches add as unique Identifier
            else:
                self.addToken(TokenType.IDENTIFIER)
        else:
            # self.had_error
            # report the error to the interpreter but do not stop the parsing
            # determine other souce of error
            raise Exception(f"unknown token at line {self.line}")

    def peekAndMatch(self, expected_lexeme):
        next_lexeme = self.peek()  # peek the next value
        if next_lexeme == expected_lexeme:
            self.advance()  # consume the next value
            return True
        else:
            return False

    def peek(self):
        return TokenType.EOF.value if self.isAtEnd() else self.source_code[self.current]

    def peekNext(self):
        return (
            TokenType.EOF.value
            if len(self.source_code) < self.current + 1
            else self.source_code[self.current + 1]
        )

    def advance(self):
        self.current += 1
        # the reason why we add first and subtract later is to use the substring fuction in the addtoken function
        # which require the end to +1'ed to get the full token
        # additionally also allows us to peek the next value without mutating or impuring the start and current variable
        return self.source_code[self.current - 1]

    def getLiteral(self):
        return self.source_code[self.start : self.current]

    def addToken(self, token, literal=None):
        ##for string, number and identifier, literal is calculated automatically for all other explicit '' need to be added
        # the following code return multicharacter lexeme, that's why start and current is required
        # lexeme = self.source_code[self.start:self.current] if literal else literal #non printable character should have None as printable literal
        self.token_list.append(
            Token(
                token,
                token.value,  # the string corresponding to the token, it is necessary only for identifier other are redundant
                self.getLiteral()
                if literal == None
                else literal,  # actual value of the tipe
                self.line,
            )
        )

    def toString(self):
        return "\n".join(map(lambda x: x.toString(), self.token_list))


class Token:
    def __init__(self, tipe, lexeme="", literal="", line=0):
        self.tipe = tipe
        self.lexeme = lexeme if lexeme else tipe.value
        self.literal = literal
        self.line = line

    def toString(self):
        return f"<TokenType: {self.tipe} | Lexeme: '{self.lexeme}' | Literal: '{self.literal}' | Line: {self.line}>"


from enum import Enum, auto


class KeywordTokens(Enum):
    ##Keywords.
    AND = "and"
    CLASS = "class"
    ELSE = "else"
    FALSE = "false"
    FUN = "fun"
    FOR = "for"
    IF = "if"
    NIL = "None"
    OR = "or"
    PRINT = "print"
    RETURN = "return"
    SUPER = "super"
    THIS = "this"
    TRUE = "true"
    VAR = "var"
    WHILE = "while"
    MATCH = "match"
    CASE = "case"
    DEFAULT = "default"
    CONTINUE = "continue"
    BREAK = "break"


class TokenType(Enum):
    ##Single-character tokens.
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    DOT = "."
    SEMICOLON = ";"
    SEPARATOR = "_"
    WALL = "|"
    MODULO = "%"

    # escape sequence token
    BACK_SLASH = "\\"
    HORIZONTAL_TAB = "\t"
    VERTICAL_TAB = "\v"
    NEW_LINE = "\n"
    CARRIAGE_RETURN = "\r"

    COMMENT = "#"
    SPACE = " "

    ##One or two character tokens.
    BANG = "!"
    BANG_EQUAL = "!="
    EQUAL = "="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="
    # syntactic sugar
    MINUS = "-"
    MINUS_EQUAL = "-="

    PLUS = "+"
    PLUS_EQUAL = "+="

    SLASH = "/"
    SLASH_EQUAL = "/="

    STAR = "*"
    STAR_EQUAL = "*="

    FAT_ARROW = "=>"

    ##Literals.
    IDENTIFIER = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    STRING = '"'
    NUMBER = "0123456789"

    ##Keywords.
    AND = KeywordTokens.AND.value
    CLASS = KeywordTokens.CLASS.value
    ELSE = KeywordTokens.ELSE.value
    FALSE = KeywordTokens.FALSE.value
    FUN = KeywordTokens.FUN.value
    FOR = KeywordTokens.FOR.value
    IF = KeywordTokens.IF.value
    NIL = KeywordTokens.NIL.value
    OR = KeywordTokens.OR.value
    PRINT = KeywordTokens.PRINT.value
    RETURN = KeywordTokens.RETURN.value
    SUPER = KeywordTokens.SUPER.value
    THIS = KeywordTokens.THIS.value
    TRUE = KeywordTokens.TRUE.value
    VAR = KeywordTokens.VAR.value
    WHILE = KeywordTokens.WHILE.value
    MATCH = KeywordTokens.MATCH.value
    CASE = KeywordTokens.CASE.value
    DEFAULT = KeywordTokens.DEFAULT.value
    CONTINUE = KeywordTokens.CONTINUE.value
    BREAK = KeywordTokens.BREAK.value

    EOF = "\0"
