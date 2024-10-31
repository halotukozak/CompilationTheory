import sys

from sly import Parser

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab1.MatrixScanner import MatrixScanner
from lab3.AST import *


class MatrixParser(Parser):
    tokens = MatrixScanner.tokens

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

    @_('instructions_opt')
    def program(self, p):
        return p.instructions_opt

    @_('instructions')
    def instructions_opt(self, p):
        return p.instructions

    @_('')
    def instructions_opt(self, p):
        return []

    @_('instruction')
    def instructions(self, p):
        return [p.instruction]

    @_('instruction instructions')
    def instructions(self, p):
        return [p.instruction] + p.instructions

    @_('statement ";"')
    def instruction(self, p):
        return p.statement

    @_('"{" instructions "}"')
    def block(self, p):
        return p.instructions

    @_('instructions')
    def block(self, p):
        return p.instructions

    @_('IF "(" condition ")" block %prec IFX')
    def instruction(self, p):
        return If(p.condition, p.block, None)

    @_('IF "(" condition ")" block ELSE block')
    def instruction(self, p):
        return If(p.condition, p.block0, p.block1)

    @_('WHILE "(" condition ")" block')
    def instruction(self, p):
        return While(p.condition, p.block)

    @_('FOR var "=" range block')
    def instruction(self, p):
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
        return Apply(SymbolRef(p[1]), [p.expr0, p.expr1])

    @_('MULASSIGN', 'DIVASSIGN', 'SUBASSIGN', 'ADDASSIGN', '"="')
    def assign_op(self, p):
        return p[0]

    @_('var assign_op expr',
       'element assign_op expr')
    def statement(self, p):
        return Assign(p[0], p.assign_op, p.expr)

    @_('matrix_function_name "(" INTNUM ")"')
    def matrix_function(self, p):
        return Apply(p.matrix_function_name, [int(p.INTNUM)])

    @_('EYE', 'ONES', 'ZEROS')
    def matrix_function_name(self, p):
        return SymbolRef(p[0])

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
        return p.vector_varargs + [int(p.INTNUM)]

    @_('INTNUM')
    def vector_varargs(self, p):
        return [int(p.INTNUM)]

    @_('vector_element', 'matrix_element')
    def element(self, p):
        return p[0]

    @_('ID "[" INTNUM "]"')
    def vector_element(self, p):
        return VectorRef(p.ID, p.INTNUM)

    @_('ID "[" INTNUM "," INTNUM "]"')
    def matrix_element(self, p):
        return MatrixRef(p.ID, int(p.INTNUM0), int(p.INTNUM1))

    @_('ID')
    def var(self, p):
        return SymbolRef(p[0])

    @_('num_expr "+" num_expr',
       'num_expr "-" num_expr',
       'num_expr "*" num_expr',
       'num_expr "/" num_expr',
       'expr DOTADD expr',
       'expr DOTSUB expr',
       'expr DOTMUL expr',
       'expr DOTDIV expr')
    def expr(self, p):
        return Apply(SymbolRef(p[1]), [p[0], p[2]])

    @_('num_expr', 'matrix', 'matrix_function', 'matrix_element', 'vector_element')
    def expr(self, p):
        return p[0]

    @_('INTNUM')
    def num_expr(self, p):
        return int(p[0])

    @_('FLOAT')
    def num_expr(self, p):
        return float(p[0])

    @_('STRING')
    def expr(self, p):
        return p[0]

    @_('var')
    def num_expr(self, p):
        return p[0]

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return Apply(SymbolRef(p[0]), p.expr)

    @_('expr "\'"')
    def expr(self, p):
        return Apply(SymbolRef(p[1]), p.expr)

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
        return Apply(SymbolRef(p[0]), p.print_args)

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
    filename = sys.argv[1] if len(sys.argv) > 1 else "example3.m"
    try:
        file = open(filename, "r")
    except IOError:
        print(f"Cannot open {filename} file")
        sys.exit(0)

    text = file.read()
    lexer = MatrixScanner()
    parser = MatrixParser()

    result = parser.parse(lexer.tokenize(text))
    for r in result:
        r.printTree()
