from sly import Lexer

from lab4.Utils import report_error


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable
class MatrixScanner(Lexer):
    tokens = {
        DOTADD, DOTSUB, DOTMUL, DOTDIV,
        ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN,
        LESS_EQUAL, GREATER_EQUAL, NOT_EQUAL, EQUAL,
        IF, ELSE, FOR, WHILE, BREAK, CONTINUE, RETURN, EYE, ZEROS, ONES, PRINT,
        ID, INTNUM, FLOAT, STRING
    }

    literals = {
        # relation operators
        '<', '>',
        # assignment operators
        '=',
        # binary operators
        '+', '-', '*', '/',
        # brackets
        '(', ')', '[', ']', '{', '}',
        # other
        ':', "'", ',', ';'
    }

    # matrix binary operators
    DOTADD = r'\.\+'
    DOTSUB = r'\.-'
    DOTMUL = r'\.\*'
    DOTDIV = r'\./'

    # relation operators
    LESS_EQUAL = r'<='
    GREATER_EQUAL = r'>='
    NOT_EQUAL = r'!='
    EQUAL = r'=='

    # assignment operators
    ADDASSIGN = r'\+='
    SUBASSIGN = r'-='
    MULASSIGN = r'\*='
    DIVASSIGN = r'/='

    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # keywords
    ID['if'] = IF
    ID['else'] = ELSE
    ID['for'] = FOR
    ID['while'] = WHILE
    ID['break'] = BREAK
    ID['continue'] = CONTINUE
    ID['return'] = RETURN
    ID['eye'] = EYE
    ID['zeros'] = ZEROS
    ID['ones'] = ONES
    ID['print'] = PRINT

    FLOAT = r'(\d+(\.\d*)|\.\d+)([eE][+-]?\d+)?'  # https://regex101.com/r/Obq7Y4/1
    INTNUM = r'[0-9]+'
    STRING = r'"[^"]*"'

    ignore = ' \t'
    ignore_comment = r'\#.*'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        report_error(self, f"Illegal character '{t.value[0]}'", self.lineno)
        self.index += 1
