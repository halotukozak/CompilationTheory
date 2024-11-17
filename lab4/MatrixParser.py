from sly import Parser
from sly.yacc import YaccProduction

from lab4.AST import *
from lab4.MatrixScanner import MatrixScanner
from lab4.Utils import report_error


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

    @_('statement \n')
    def instruction(self, p: YaccProduction):
        report_error(self, "Missing semicolon", p.lineno)

    @_('"{" instructions "}"')
    def block(self, p: YaccProduction):
        return p.instructions

    @_('"(" expr ")"')
    def expr(self, p: YaccProduction):
        return p.expr

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

    @_('expr ":" expr')
    def range(self, p: YaccProduction):
        return Range(p.expr0, p.expr1, p.lineno)

    @_('EQUAL', 'NOT_EQUAL', 'LESS_EQUAL', 'GREATER_EQUAL', '">"', '"<"', )
    def comparator(self, p: YaccProduction):
        return p[0]

    @_('expr comparator expr')
    def condition(self, p: YaccProduction):
        return Apply(SymbolRef(p.comparator, p.lineno), [p.expr0, p.expr1], p.lineno)

    @_('MULASSIGN', 'DIVASSIGN', 'SUBASSIGN', 'ADDASSIGN', '"="')
    def assign_op(self, p: YaccProduction):
        return p[0]

    @_('element assign_op expr',
       'var assign_op expr')
    def statement(self, p: YaccProduction):
        return Assign(p[0], p.assign_op, p.expr, p.lineno)

    @_('function_name "(" var_args ")"')
    def expr(self, p: YaccProduction):
        return Apply(p.function_name, p.var_args, p.lineno)

    @_('EYE', 'ONES', 'ZEROS', 'ID')
    def function_name(self, p: YaccProduction):
        return SymbolRef(p[0], p.lineno)

    @_('"[" var_args "]"')
    def matrix(self, p: YaccProduction):
        return Apply(SymbolRef("init_matrix_or_vector", p.lineno), p.var_args, p.lineno)

    @_('var "[" var_args "]"')
    def element(self, p: YaccProduction):
        match len(p.var_args):
            case 1:
                return VectorRef(p.var, p.var_args[0], p.lineno)
            case 2:
                return MatrixRef(p.var, p.var_args[0], p.var_args[1], p.lineno)
            case _:
                report_error(self, "Invalid matrix element reference", p.lineno)

    @_('ID')
    def var(self, p: YaccProduction):
        return SymbolRef(p[0], p.lineno)

    @_('expr "+" expr',
       'expr "-" expr',
       'expr "*" expr',
       'expr "/" expr',
       'expr DOTADD expr',
       'expr DOTSUB expr',
       'expr DOTMUL expr',
       'expr DOTDIV expr')
    def expr(self, p: YaccProduction):
        return Apply(SymbolRef(p[1], p.lineno), [p.expr0, p.expr1], p.lineno)

    @_('var', 'matrix', 'element')
    def expr(self, p: YaccProduction):
        return p[0]

    @_('INTNUM')
    def expr(self, p: YaccProduction):
        return Literal.int(p[0], p.lineno)

    @_('FLOAT')
    def expr(self, p: YaccProduction):
        return Literal.float(p[0], p.lineno)

    @_('STRING')
    def expr(self, p: YaccProduction):
        return Literal.string(p[0], p.lineno)

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

    @_('PRINT var_args')
    def statement(self, p: YaccProduction):
        return Apply(SymbolRef(p[0], p.lineno), p.var_args, p.lineno)

    @_('var_args "," expr')
    def var_args(self, p: YaccProduction):
        return p.var_args + [p.expr]

    @_('expr')
    def var_args(self, p: YaccProduction):
        return [p.expr]

    def error(self, p: YaccProduction):
        if p:
            report_error(self, f"Syntax error: {p.type}('{p.value}')", p.lineno)
        else:
            report_error(self, "Syntax error", -1)
