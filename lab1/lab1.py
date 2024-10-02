import sys

from sly import Lexer


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable
class MatrixScanner(Lexer):
    tokens = {
        PLUS, MINUS, TIMES, DIVIDE,
        PLUS_DOT, MINUS_DOT, TIMES_DOT, DIVIDE_DOT,
        ASSIGN, PLUS_ASSIGN, MINUS_ASSIGN, TIMES_ASSIGN, DIVIDE_ASSIGN,
        LESS, GREATER, LESS_EQUAL, GREATER_EQUAL, NOT_EQUAL, EQUAL,
        LPAREN, RPAREN, LBRACKET, RBRACKET, LBRACE, RBRACE,
        RANGE, TRANSPOSE, COMMA, SEMICOLON,
        IF, ELSE, FOR, WHILE, BREAK, CONTINUE, RETURN, EYE, ZEROS, ONES, PRINT,
        ID, INT, FLOAT, STRING
    }

    # matrix binary operators
    PLUS_DOT = r'\.\+'
    MINUS_DOT = r'\.-'
    TIMES_DOT = r'\.\*'
    DIVIDE_DOT = r'\./'

    # relation operators
    LESS_EQUAL = r'<='
    GREATER_EQUAL = r'>='
    LESS = r'<'
    GREATER = r'>'
    NOT_EQUAL = r'!='
    EQUAL = r'=='

    # assignment operators
    ASSIGN = r'='
    PLUS_ASSIGN = r'\+='
    MINUS_ASSIGN = r'-='
    TIMES_ASSIGN = r'\*='
    DIVIDE_ASSIGN = r'/='

    # binary operators
    PLUS = '\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'

    # brackets
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    LBRACE = r'\{'
    RBRACE = r'\}'

    # other
    RANGE = r':'
    TRANSPOSE = r"'"
    COMMA = r','
    SEMICOLON = r';'

    # keywords
    IF = r'if'
    ELSE = r'else'
    FOR = r'for'
    WHILE = r'while'
    BREAK = r'break'
    CONTINUE = r'continue'
    RETURN = r'return'
    EYE = r'eye'
    ZEROS = r'zeros'
    ONES = r'ones'
    PRINT = r'print'

    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    FLOAT = r'[+-]?(\d+\.\d+|\.\d+|\d+\.)'
    INT = r'[+-]?[0-9]+'
    STRING = r'".*"'

    ignore = ' \t'
    ignore_comment = r'\#.*'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1


if __name__ == '__main__':
    try:
        # filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
        filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()
    lexer = MatrixScanner()

    for token in lexer.tokenize(text):
        print(f"({token.lineno}): {token.type}({token.value})")
