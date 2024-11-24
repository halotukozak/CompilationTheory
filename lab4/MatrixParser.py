from sly import Parser
from sly.yacc import YaccProduction

from lab4 import AST
from lab4 import Predef
from lab4 import TypeSystem as TS
from lab4.MatrixScanner import MatrixScanner
from lab4.Utils import report_error
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
    def instructions_opt(self, _: YaccProduction):
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
        return AST.If(p.condition, p.block, None, p.lineno)

    @_('IF "(" condition ")" block ELSE block')
    def instruction(self, p: YaccProduction):
        return AST.If(p.condition, p.block0, p.block1, p.lineno)

    @_('WHILE "(" condition ")" block')
    def instruction(self, p: YaccProduction):
        return AST.While(p.condition, p.block, p.lineno)

    @_('FOR ID "=" range block')
    def instruction(self, p: YaccProduction):
        var = AST.SymbolRef(p.ID, p.lineno, TS.Int())
        return AST.For(var, p.range, p.block, p.lineno)

    @_('expr ":" expr')
    def range(self, p: YaccProduction):
        return AST.Range(p.expr0, p.expr1, p.lineno)

    @_('EQUAL', 'NOT_EQUAL', 'LESS_EQUAL', 'GREATER_EQUAL', '">"', '"<"')
    def comparator(self, p: YaccProduction):
        return p[0]

    @_('expr comparator expr')
    def condition(self, p: YaccProduction):
        args = [p.expr0, p.expr1]
        return AST.Apply(Predef.get_symbol(p.comparator), args, p[0].lineno)

    @_('MULASSIGN', 'DIVASSIGN', 'SUBASSIGN', 'ADDASSIGN', '"="')
    def assign_op(self, p: YaccProduction):
        return p[0]

    @_('element assign_op expr')
    def statement(self, p: YaccProduction):
        match p.assign_op:
            case "=":
                expr = p.expr
            case _:
                args = [p.element, p.expr]
                expr = AST.Apply(Predef.get_symbol(p.assign_op[:-1]), args, p.lineno)
        return AST.Assign(p.element, expr, p.lineno)

    @_('ID assign_op expr')
    def statement(self, p: YaccProduction):
        var = AST.SymbolRef(p.ID, p.lineno, TS.undef())
        match p.assign_op:
            case "=":
                expr = p.expr
            case _:
                expr = AST.Apply(Predef.get_symbol(p.assign_op[:-1]), [var, p.expr], p.lineno)
        var.type = expr.type
        return AST.Assign(var, expr, p.lineno)

    @_('function_name "(" var_args ")"')
    def expr(self, p: YaccProduction):
        return AST.Apply(Predef.get_symbol(p.function_name), p.var_args, p.lineno)

    @_('EYE', 'ONES', 'ZEROS')
    def function_name(self, p: YaccProduction):
        return p[0]

    @_('"[" var_args "]"')
    def matrix(self, p: YaccProduction):
        return AST.Apply(Predef.get_symbol("INIT"), p.var_args, p.lineno)

    @_('var "[" var_args "]"')
    def element(self, p: YaccProduction):
        match len(p.var_args):
            case 1:
                return AST.VectorRef(p.var, p.var_args[0], p.lineno)
            case 2:
                return AST.MatrixRef(p.var, p.var_args[0], p.var_args[1], p.lineno)
            case _:
                report_error(self, "Invalid matrix element reference", p.lineno)
                return AST.MatrixRef(p.var, None, None, p.lineno)

    @_('ID')
    def var(self, p: YaccProduction):
        return AST.SymbolRef(p[0], p.lineno, TS.undef())

    @_('expr "+" expr',
       'expr "-" expr',
       'expr "*" expr',
       'expr "/" expr',
       'expr DOTADD expr',
       'expr DOTSUB expr',
       'expr DOTMUL expr',
       'expr DOTDIV expr')
    def expr(self, p: YaccProduction):
        return AST.Apply(Predef.get_symbol(p[1]), [p.expr0, p.expr1], p.lineno)

    @_('var', 'matrix', 'element')
    def expr(self, p: YaccProduction):
        return p[0]

    @_('INTNUM')
    def expr(self, p: YaccProduction):
        return AST.Literal.int(p[0], p.lineno)

    @_('FLOAT')
    def expr(self, p: YaccProduction):
        return AST.Literal.float(p[0], p.lineno)

    @_('STRING')
    def expr(self, p: YaccProduction):
        return AST.Literal.string(p[0], p.lineno)

    @_('"-" expr %prec UMINUS')
    def expr(self, p: YaccProduction):
        args = [p.expr]
        return AST.Apply(Predef.get_symbol("UMINUS"), args, p.lineno)

    @_('expr "\'"')
    def expr(self, p: YaccProduction):
        args = [p.expr]
        return AST.Apply(Predef.get_symbol("'"), args, p.lineno)

    @_('BREAK')
    def statement(self, p: YaccProduction):
        return AST.Break(p.lineno)

    @_('CONTINUE')
    def statement(self, p: YaccProduction):
        return AST.Continue(p.lineno)

    @_('RETURN expr')
    def statement(self, p: YaccProduction):
        return AST.Return(p.expr, p.lineno)

    @_('PRINT var_args')
    def statement(self, p: YaccProduction):
        args = p.var_args
        return AST.Apply(Predef.get_symbol("PRINT"), args, p.lineno)

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

# [Assign(var=SymbolRef(name='x', lineno=2, type=undef), expr=Literal(value=1, lineno=2, type=Int), lineno=2), Assign(var=SymbolRef(name='z', lineno=3, type=undef), expr=SymbolRef(name='x', lineno=3, type=undef), lineno=3), Assign(var=SymbolRef(name='z', lineno=4, type=undef), expr=Apply(fun=SymbolRef(name='+', lineno=None, type=Int | Float), args=[SymbolRef(name='z', lineno=4, type=undef), Literal(value=1, lineno=4, type=Int)], lineno=4), lineno=4), While(condition=Apply(fun=SymbolRef(name='<=', lineno=None, type=Bool), args=[SymbolRef(name='x', lineno=6, type=undef), Literal(value=0, lineno=6, type=Int)], lineno=6), body=[Assign(var=SymbolRef(name='undef_outside_scope', lineno=7, type=undef), expr=SymbolRef(name='x', lineno=7, type=undef), lineno=7)], lineno=6), While(condition=Apply(fun=SymbolRef(name='<=', lineno=None, type=Bool), args=[SymbolRef(name='undef', lineno=10, type=undef), Literal(value=0, lineno=10, type=Int)], lineno=10), body=[Assign(var=SymbolRef(name='undef_outside_scope', lineno=11, type=undef), expr=SymbolRef(name='undef', lineno=11, type=undef), lineno=11)], lineno=10), Assign(var=SymbolRef(name='M', lineno=14, type=undef), expr=Literal(value=5, lineno=14, type=Int), lineno=14), For(var=SymbolRef(name='j', lineno=16, type=Int), range=Range(start=SymbolRef(name='undef', lineno=16, type=undef), end=SymbolRef(name='M', lineno=16, type=undef), lineno=16), body=[Apply(fun=SymbolRef(name='PRINT', lineno=None, type=undef), args=[SymbolRef(name='undef', lineno=17, type=undef), SymbolRef(name='j', lineno=17, type=undef)], lineno=17)], lineno=16), Assign(var=SymbolRef(name='x', lineno=20, type=undef), expr=SymbolRef(name='undef_outside_scope', lineno=20, type=undef), lineno=20)]
