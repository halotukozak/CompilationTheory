import sys

from prompt_toolkit.contrib.regular_languages.regex_parser import Variable
from sly import Parser

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab1.MatrixScanner import MatrixScanner
from lab3.AST import *


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable
class MatrixParser(Parser):
    tokens = MatrixScanner.tokens

    start = 'program'
    debugfile = 'parser.out'

    precedence = (
        ('nonassoc', 'IFX'),
        ('nonassoc', 'ELSE'),
        ('right', 'MULASSIGN', 'DIVASSIGN', 'SUBASSIGN', 'ADDASSIGN'),
        ('nonassoc', '<', '>', 'LESS_EQUAL', 'GREATER_EQUAL', 'NOT_EQUAL', 'EQUAL'),
        ('left', '+', '-'),
        ('left', 'DOTADD', 'DOTSUB'),
        ('left', '*', '/'),
        ('left', 'DOTMUL', 'DOTDIV'),
        ('right', 'UMINUS'),
        ('left', "'"),
    )

    @_('blocks_opt')
    def program(self, p):
        pass

    @_('blocks')
    def blocks_opt(self, p):
        pass

    @_('')
    def blocks_opt(self, p):
        pass

    @_('block')
    def blocks(self, p):
        return Block(p.block)

    @_('block blocks')
    def blocks(self, p):
        pass

    @_('assignment ";"',
       'statement ";"',
       '"{" blocks "}"')
    def block(self, p):
        return block(p[0])

    @_('IF "(" condition ")" block %prec IFX')
    def block(self, p):
        return IF(p.condition, p.block, None)

    @_('IF "(" condition ")" block ELSE block')
    def block(self, p):
        return IF(p.condition, p.block0, p.block1)

    @_('WHILE "(" condition ")" block')
    def block(self, p):
        return WHILE(p.condition, p.block)

    @_('FOR var "=" range block')
    def block(self, p):
        return FOR(p.var, p.range, p.block)

    @_('expression ":" expression')
    def range(self, p):
        return Range(p[0], p[1])

    @_('expression EQUAL expression',
       'expression NOT_EQUAL expression',
       'expression LESS_EQUAL expression',
       'expression GREATER_EQUAL expression',
       'expression "<" expression',
       'expression ">" expression')
    def condition(self, p):
        return Condition(p.expression0, p[1], p.expression1)

    @_('MULASSIGN', 'DIVASSIGN', 'SUBASSIGN', 'ADDASSIGN', '"="')
    def assignment_op(self, p):
        return AssignmentOperator(p[0])

    @_('var assignment_op expression',
       'element assignment_op expression')
    def assignment(self, p):
        return Assignment(p[0], p.assignment_op, p.expression)

    @_('matrix_function_name "(" INTNUM ")"')
    def matrix_function(self, p):
        pass

    @_('EYE', 'ONES', 'ZEROS')
    def matrix_function_name(self, p):
        pass

    @_('"[" vectors "]"')
    def matrix(self, p):
        pass

    @_('vectors "," vector',
       'vector')
    def vectors(self, p):
        pass

    @_('"[" variables "]"')
    def vector(self, p):
        pass

    @_('variables "," variable',
       'variable')
    def variables(self, p):
        pass

    @_('number', 'var', 'element')
    def variable(self, p):
        return Variable(p[0])

    @_('vector_element', 'matrix_element')
    def element(self, p):
        pass

    @_('ID "[" INTNUM "]"')
    def vector_element(self, p):
        pass

    @_('ID "[" INTNUM "," INTNUM "]"')
    def matrix_element(self, p):
        pass

    @_('ID')
    def var(self, p):
        return Var(p[0])

    @_('INTNUM', 'FLOAT')
    def number(self, p):
        return Number(p[0])

    @_('STRING')
    def string(self, p):
        return String(p[0])

    @_('expression "+" expression',
       'expression "-" expression',
       'expression "*" expression',
       'expression "/" expression',
       'expression DOTADD expression',
       'expression DOTSUB expression',
       'expression DOTMUL expression',
       'expression DOTDIV expression')
    def expression(self, p):
        return BinaryOperator(p[1], p.expr0, p.expr1)

    @_('num_expression', 'matrix', 'matrix_function', 'uminus', 'transposition', 'matrix_element', 'vector_element')
    def expression(self, p):
        return Expr(p[0])

    @_('number', 'var')
    def num_expression(self, p):
        pass

    @_('"-" expression %prec UMINUS')
    def expression(self, p):
        return UnaryOperator(p[0], p.expression)

    @_('expression "\'"')
    def expression(self, p):
        return UnaryOperator(p.expression, p[1])

    @_('BREAK')
    def statement(self, p):
        return Break

    @_('CONTINUE')
    def statement(self, p):
        return CONTINUE

    @_('RETURN expression')
    def statement(self, p):
        return Return(p.expression)

    @_('PRINT print_vals')
    def statement(self, p):
        return PRINT(p[0])

    @_('print_vals "," print_val',
       'print_val')
    def print_vals(self, p):
        pass

    @_('string', 'expression')
    def print_val(self, p):
        pass

    # Error handling
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

    parser.parse(lexer.tokenize(text))
