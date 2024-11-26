import sys

from lab5 import Utils
from lab5.MatrixParser import MatrixParser
from lab5.MatrixScanner import MatrixScanner
from lab5.MatrixScoper import MatrixScoper
from lab5.MatrixTypeChecker import MatrixTypeChecker
from lab5.TreePrinter import TreePrinter
from lab5.Utils import print_errors_and_warnings

if __name__ == '__main__':
    name = "examples/test.m"
    filename = sys.argv[1] if len(sys.argv) > 1 else name
    try:
        file = open(filename, "r")
    except IOError:
        print(f"Cannot open {filename} file")
        sys.exit(0)


    def quit_if_failed(self):
        if getattr(self, 'failed', False):
            print_errors_and_warnings()
            sys.exit(0)


    Utils.debug = True

    print_ast = False

    text = file.read()
    lexer = MatrixScanner()
    tokens = lexer.tokenize(text)
    quit_if_failed(lexer)

    parser = MatrixParser()
    ast = parser.parse(tokens)
    quit_if_failed(parser)

    if print_ast:
        treePrinter = TreePrinter()
        treePrinter.print_result(ast)

    scoper = MatrixScoper()
    scoper.visit_all(ast)
    # print(ast)
    type_checker = MatrixTypeChecker()
    type_checker.visit_all(ast)
    # print(ast)
    quit_if_failed(type_checker)
