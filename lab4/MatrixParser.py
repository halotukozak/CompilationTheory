from sly import Parser
from sly.yacc import YaccProduction

from lab4.AST import *
from lab4.MatrixScanner import MatrixScanner


# noinspection PyUnresolvedReferences
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
    def program(self, p: YaccProduction):
        return p.instructions_opt

    @_('instructions')
    def instructions_opt(self, p: YaccProduction):
        return p.instructions

    @_('')
    def instructions_opt(self, p: YaccProduction):
        return []

    @_('instruction')
    def instructions(self, p: YaccProduction):
        return [p.instruction]

    @_('instruction instructions')
    def instructions(self, p: YaccProduction):
        return [p.instruction] + p.instructions

    @_('statement ";"')
    def instruction(self, p: YaccProduction):
        return p.statement

    @_('"{" instructions "}"')
    def block(self, p: YaccProduction):
        return p.instructions

    @_('instruction')
    def block(self, p: YaccProduction):
        return [p.instruction]

    @_('IF "(" condition ")" block %prec IFX')
    def instruction(self, p: YaccProduction):
        return If(p.condition, p.block, None, p.lineno)

    @_('IF "(" condition ")" block ELSE block')
    def instruction(self, p: YaccProduction):
        return If(p.condition, p.block0, p.block1, p.lineno)

    @_('WHILE "(" condition ")" block')
    def instruction(self, p: YaccProduction):
        return While(p.condition, p.block, p.lineno)

    @_('FOR var "=" range block')
    def instruction(self, p: YaccProduction):
        return For(p.var, p.range, p.block, p.lineno)

    @_('num_expr ":" num_expr')
    def range(self, p: YaccProduction):
        return Range(p.num_expr0, p.num_expr1, p.lineno)

    @_('expr EQUAL expr',
       'expr NOT_EQUAL expr',
       'expr LESS_EQUAL expr',
       'expr GREATER_EQUAL expr',
       'expr "<" expr',
       'expr ">" expr')
    def condition(self, p: YaccProduction):
        return Apply(SymbolRef(p[1], p.lineno), [p.expr0, p.expr1], p.lineno)

    @_('MULASSIGN', 'DIVASSIGN', 'SUBASSIGN', 'ADDASSIGN', '"="')
    def assign_op(self, p: YaccProduction):
        return p[0]

    @_('var assign_op expr')
    def statement(self, p: YaccProduction):
        return Assign(p.var, p.assign_op, p.expr, p.lineno)

    @_('element assign_op expr')
    def statement(self, p: YaccProduction):
        return Assign(p.element, p.assign_op, p.expr, p.lineno)

    @_('matrix_function_name "(" INTNUM ")"')
    def matrix_function(self, p: YaccProduction):
        return Apply(p.matrix_function_name, [Literal.int(p.INTNUM, p.lineno)], p.lineno)

    @_('EYE', 'ONES', 'ZEROS')
    def matrix_function_name(self, p: YaccProduction):
        return SymbolRef(p[0], p.lineno)

    @_('"[" matrix_varargs "]"')
    def matrix(self, p: YaccProduction):
        return Matrix(p.matrix_varargs, p.lineno)

    @_('matrix_varargs "," vector')
    def matrix_varargs(self, p: YaccProduction):
        return p.matrix_varargs + [p.vector]

    @_('vector')
    def matrix_varargs(self, p: YaccProduction):
        return [p.vector]

    @_('"[" vector_varargs "]"')
    def vector(self, p: YaccProduction):
        return Vector(p.vector_varargs, p.lineno)

    @_('vector_varargs "," INTNUM')
    def vector_varargs(self, p: YaccProduction):
        return p.vector_varargs + [Literal.int(p.INTNUM, p.lineno)]

    @_('INTNUM')
    def vector_varargs(self, p: YaccProduction):
        return [Literal.int(p.INTNUM, p.lineno)]

    @_('vector_element', 'matrix_element')
    def element(self, p: YaccProduction):
        return p[0]

    @_('ID "[" INTNUM "]"')
    def vector_element(self, p: YaccProduction):
        return VectorRef(SymbolRef(p.ID, p.lineno), Literal.int(p.INTNUM, p.lineno), p.lineno)

    @_('ID "[" INTNUM "," INTNUM "]"')
    def matrix_element(self, p: YaccProduction):
        return MatrixRef(SymbolRef(p.ID, p.lineno), Literal.int(p.INTNUM0, p.lineno), Literal.int(p.INTNUM1, p.lineno),
                         p.lineno)

    @_('ID')
    def var(self, p: YaccProduction):
        return SymbolRef(p[0], p.lineno)

    @_('num_expr "+" num_expr',
       'num_expr "-" num_expr',
       'num_expr "*" num_expr',
       'num_expr "/" num_expr',
       'expr DOTADD expr',
       'expr DOTSUB expr',
       'expr DOTMUL expr',
       'expr DOTDIV expr')
    def expr(self, p: YaccProduction):
        return Apply(SymbolRef(p[1], p.lineno), [p[0], p[2]], p.lineno)

    @_('num_expr', 'matrix', 'matrix_function', 'matrix_element', 'vector_element', 'STRING')
    def expr(self, p: YaccProduction):
        return p[0]

    @_('INTNUM')
    def num_expr(self, p: YaccProduction):
        return Literal.int(p[0], p.lineno)

    @_('FLOAT')
    def num_expr(self, p: YaccProduction):
        return Literal.float(p[0], p.lineno)

    @_('var')
    def num_expr(self, p: YaccProduction):
        return p.var

    @_('"-" expr %prec UMINUS')
    def expr(self, p: YaccProduction):
        return Apply(SymbolRef(p[0], p.lineno), [p.expr], p.lineno)

    @_('expr "\'"')
    def expr(self, p: YaccProduction):
        return Apply(SymbolRef(p[1], p.lineno), [p.expr], p.lineno)

    @_('BREAK')
    def statement(self, p: YaccProduction):
        return Break(p.lineno)

    @_('CONTINUE')
    def statement(self, p: YaccProduction):
        return Continue(p.lineno)

    @_('RETURN expr')
    def statement(self, p: YaccProduction):
        return Return(p.expr, p.lineno)

    @_('PRINT print_args')
    def statement(self, p: YaccProduction):
        return Apply(SymbolRef(p[0], p.lineno), p.print_args, p.lineno)

    @_('print_args "," expr')
    def print_args(self, p: YaccProduction):
        return p.print_args + [p.expr]

    @_('expr')
    def print_args(self, p: YaccProduction):
        return [p.expr]

    def error(self, p: YaccProduction):
        if p:
            print(f"Syntax error at line {p.lineno}: {p.type}('{p.value}')")
        else:
            print("Unexpected end of input")
