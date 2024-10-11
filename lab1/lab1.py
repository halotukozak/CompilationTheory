import sys

from sly import Lexer


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

    FLOAT = r'[+-]?(\d+(\.\d*)([eE][+-]?\d+)?|\.\d+([eE][+-]?\d+)?)' # https://regex101.com/r/Obq7Y4/1
    INTNUM = r'[+-]?[0-9]+'  
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
        filename = sys.argv[1] if len(sys.argv) > 1 else "/home/fabio/Documents/kompilatory/CompilationTheory/lab1/example_full.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()
    lexer = MatrixScanner()

    for token in lexer.tokenize(text):
        print(f"({token.lineno}): {token.type}({token.value})")
