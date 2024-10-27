import sys

import os
from sly import Parser
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab1.MatrixScanner import MatrixScanner


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable
class MatrixParser(Parser):
    tokens = MatrixScanner.tokens

    start = 'program'

    # Precedence rules (similar structure to PLY)
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

    @_('instructions_opt')
    def program(self, p):
        pass

    @_('instructions')
    def instructions_opt(self, p):
        pass

    @_('')
    def instructions_opt(self, p):
        pass

    @_('instruction')
    def instructions(self, p):
        pass

    @_('instruction instructions')
    def instructions(self, p):
        pass

    @_('assignment ";"',
       'statement ";"',
       '"{" instructions "}"')
    def instruction(self, p):
        pass

    @_('IF "(" condition ")" instruction %prec IFX')
    def instruction(self, p):
        pass

    @_('IF "(" condition ")" instruction ELSE instruction')
    def instruction(self, p):
        pass

    @_('WHILE "(" condition ")" instruction')
    def instruction(self, p):
        pass

    @_('FOR var "=" range instruction')
    def instruction(self, p):
        pass

    @_('expression ":" expression')
    def range(self, p):
        pass

    @_('expression EQUAL expression',
       'expression NOT_EQUAL expression',
       'expression LESS_EQUAL expression',
       'expression GREATER_EQUAL expression',
       'expression "<" expression',
       'expression ">" expression')
    def condition(self, p):
        pass

    @_('MULASSIGN', 'DIVASSIGN', 'SUBASSIGN', 'ADDASSIGN', '"="')
    def assignment_op(self, p):
        pass

    @_('var assignment_op expression',
       'matrix_element assignment_op expression',
       'vector_element assignment_op expression')
    def assignment(self, p):
        pass

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
        pass

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
        pass

    @_('INTNUM', 'FLOAT')
    def number(self, p):
        pass

    @_('STRING')
    def string(self, p):
        pass

    @_('expression "+" expression',
       'expression "-" expression',
       'expression "*" expression',
       'expression "/" expression',
       'expression DOTADD expression',
       'expression DOTSUB expression',
       'expression DOTMUL expression',
       'expression DOTDIV expression')
    def expression(self, p):
        pass

    @_('num_expression', 'matrix', 'matrix_function', 'uminus', 'transposition', 'matrix_element', 'vector_element')
    def expression(self, p):
        pass

    @_('number', 'var')
    def num_expression(self, p):
        pass

    @_('"-" expression %prec UMINUS')
    def uminus(self, p):
        pass

    @_('expression "\'"')
    def transposition(self, p):
        pass

    @_('BREAK')
    def statement(self, p):
        pass

    @_('CONTINUE')
    def statement(self, p):
        pass

    @_('RETURN expression')
    def statement(self, p):
        pass

    @_('PRINT print_vals')
    def statement(self, p):
        pass

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
        filename = sys.argv[1] if len(sys.argv) > 1 else "lab2/example3.m"
        file = open(filename, "r")
    except IOError:
        print(f"Cannot open {filename} file")
        sys.exit(0)

    text = file.read()
    lexer = MatrixScanner()
    parser = MatrixParser()

    parser.parse(lexer.tokenize(text))
