import sys

from sly import Parser

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab1.MatrixScanner import MatrixScanner
from lab3.AST import *


class MatrixParser(Parser):
    tokens = MatrixScanner.tokens

    start = 'program'
    debugfile = 'parser.out'

    precedence = (
        ('nonassoc', 'IFX'),
        ('nonassoc', 'ELSE'),
        ('nonassoc', '<', '>', 'LESS_EQUAL', 'GREATER_EQUAL', 'NOT_EQUAL', 'EQUAL'),
        ('left', '+', '-'),
        ('left', 'DOTADD', 'DOTSUB'),
        ('left', '*', '/'),
        ('left', 'DOTMUL', 'DOTDIV'),
        ('right', 'UMINUS'),
        ('left', "'"),
    )

    @_('statements')
    def program(self, p):
        return Block(p.statements)

    @_('')
    def statement(self, p):
        return []

    @_('statements ";" statement')
    def statements(self, p):
        return p.statements + [p.statement]

    @_('"{" statements "}"')
    def statements(self, p):
        return p.statements

    @_('statements')
    def block(self, p):
        return Block(p.statements)

    @_('IF "(" condition ")" block %prec IFX')
    def statement(self, p):
        return If(p.condition, p.block, None)

    @_('IF "(" condition ")" block ELSE block')
    def statement(self, p):
        return If(p.condition, p.block0, p.block1)

    @_('WHILE "(" condition ")" block')
    def statement(self, p):
        return While(p.condition, p.block)

    @_('FOR var "=" range block')
    def statement(self, p):
        return For(p.var, p.range, p.block)

    @_('num_expr ":" num_expr')
    def range(self, p):
        return Range(p.num_expr0, p.num_expr1)

    @_('expr EQUAL expr',
       'expr NOT_EQUAL expr',
       'expr LESS_EQUAL expr',
       'expr GREATER_EQUAL expr',
       'expr "<" expr',
       'expr ">" expr')
    def condition(self, p):
        return Apply(p[1], [p.expr0, p.expr1])

    @_('MULASSIGN', 'DIVASSIGN', 'SUBASSIGN', 'ADDASSIGN', '"="')
    def assign_op(self, p):
        return p[0]

    @_('var assign_op expr',
       'element assign_op expr')
    def statement(self, p):
        return Assign(p[0], p.assign_op, p.expr)

    @_('matrix_function_name "(" INTNUM ")"')
    def matrix_function(self, p):
        return Apply(p.matrix_function_name, [p.INTNUM])

    @_('EYE', 'ONES', 'ZEROS')
    def matrix_function_name(self, p):
        return Ref(p[0])

    @_('"[" matrix_varargs "]"')
    def matrix(self, p):
        return Matrix(p.matrix_varargs)

    @_('matrix_varargs "," vector')
    def matrix_varargs(self, p):
        return p.matrix_varargs + [p.vector]

    @_('vector')
    def matrix_varargs(self, p):
        return [p.vector]

    @_('"[" vector_varargs "]"')
    def vector(self, p):
        return Vector(p.vector_varargs)

    @_('vector_varargs "," INTNUM')
    def vector_varargs(self, p):
        return p.vector_varargs + [p.INTNUM]

    @_('INTNUM')
    def vector_varargs(self, p):
        return [p.INTNUM]

    @_('vector_element', 'matrix_element')
    def element(self, p):
        return Ref(p[0])

    @_('ID "[" INTNUM "]"')
    def vector_element(self, p):
        return VectorRef(p.ID, p.INTNUM)

    @_('ID "[" INTNUM "," INTNUM "]"')
    def matrix_element(self, p):
        return MatrixRef(p.ID, p.INTNUM0, p.INTNUM1)

    @_('ID')
    def var(self, p):
        return Ref(p[0])

    @_('INTNUM', 'FLOAT')
    def number(self, p):
        return p[0]

    @_('STRING')
    def expr(self, p):
        return p[0]

    @_('num_expr "+" num_expr',
       'num_expr "-" num_expr',
       'num_expr "*" num_expr',
       'num_expr "/" num_expr',
       'expr DOTADD expr',
       'expr DOTSUB expr',
       'expr DOTMUL expr',
       'expr DOTDIV expr')
    def expr(self, p):
        return Apply(Ref(p[1]), [p[0], p[2]])

    @_('num_expr', 'matrix', 'matrix_function', 'matrix_element', 'vector_element')
    def expr(self, p):
        return p[0]

    @_('number', 'var')
    def num_expr(self, p):
        return p[0]

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return Apply(Ref(p[0]), p.expr)

    @_('expr "\'"')
    def expr(self, p):
        return Apply(Ref(p[1]), p.expr)

    @_('BREAK')
    def statement(self, p):
        return Break

    @_('CONTINUE')
    def statement(self, p):
        return Continue

    @_('RETURN expr')
    def statement(self, p):
        return Return(p.expr)

    @_('PRINT print_args')
    def statement(self, p):
        return Apply(Ref(p[0]), p.print_args)

    @_('print_args "," expr')
    def print_args(self, p):
        return p.print_args + [p.expr]

    @_('expr')
    def print_args(self, p):
        return [p.expr]

    def error(self, p):
        if p:
            print(f"Syntax error at line {p.lineno}: {p.type}('{p.value}')")
        else:
            print("Unexpected end of input")


if __name__ == '__main__':
    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "example3.m"
        file = open(filename, "r")
    except IOError:
        print(f"Cannot open {filename} file")
        sys.exit(0)

    text = file.read()
    lexer = MatrixScanner()
    parser = MatrixParser()

    result = parser.parse(lexer.tokenize(text))
    result.printTree()