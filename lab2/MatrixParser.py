import sys

from sly import Parser

from lab1.MatrixScanner import MatrixScanner


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable
class MatrixParser(Parser):
    tokens = MatrixScanner.tokens

    precedence = (
        ("left", '+', '-'),
        ("left", '*', '/'),
        ("left", 'DOTADD', 'DOTSUB', 'DOTMUL', 'DOTDIV'),
    )

    def __init__(self):
        self.id = {}

    @_('term')
    def expr(self, p):
        return p.term

    @_('factor')
    def term(self, p):
        return p.factor

    @_('INTNUM')
    def factor(self, p):
        return p.INTNUM

    @_('FLOAT')
    def factor(self, p):
        return p.FLOAT

    @_('ID')
    def expr(self, p):
        try:
            return self.id[p.NAME]
        except LookupError:
            print("Undefined name '%s'" % p.id)
            return 0

    @_('ID "=" expr')
    def statement(self, p):
        self.id[p.ID] = p.expr

    @_('ID "=" special_function')
    def statement(self, p):
        self.id[p.ID] = p.special_function

    @_('ZEROS "(" INTNUM ")"')
    def special_function(self, p):
        return [[0] * p.INTNUM for _ in range(p.INTNUM)]

    @_('ONES "(" INTNUM ")"')
    def special_function(self, p):
        return [[1] * p.INTNUM for _ in range(p.INTNUM)]

    @_('EYE "(" INTNUM ")"')
    def special_function(self, p):
        size = p.INTNUM
        return [[1 if i == j else 0 for i in range(size)] for j in range(size)]


    @_('expr "+" term')
    def expr(self, p):
        return p.expr + p.term

    @_('expr "-" term')
    def expr(self, p):
        return p.expr - p.term

    @_('expr "*" term')
    def expr(self, p):
        return p.expr + p.term

    @_('expr "/" term')
    def expr(self, p):
        return p.expr / p.term

    def error(self, p):
        if p:
            print(f"Syntax error at line {p.lineno}: unexpected token {p.value}")
        else:
            print("Syntax error at EOF")


if __name__ == '__main__':
    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "example1.m"
        file = open(filename, "r")
    except IOError:
        print(f"Cannot open {filename} file")
        sys.exit(0)

    text = file.read()
    lexer = MatrixScanner()
    parser = MatrixParser()

    parser.parse(lexer.tokenize(text))
