import sys

from lab4.MatrixParser import MatrixParser
from lab4.MatrixScanner import MatrixScanner
from lab4.MatrixScoper import MatrixScoper
from lab4.MatrixTypeChecker import MatrixTypeChecker
from lab4.Utils import print_errors_and_warnings

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


    text = file.read()
    lexer = MatrixScanner()
    tokens = lexer.tokenize(text)
    quit_if_failed(lexer)

    parser = MatrixParser()
    ast = parser.parse(tokens)
    quit_if_failed(parser)
    # treePrinter = TreePrinter()
    # treePrinter.print_result(result)

    scoper = MatrixScoper()
    scoper.visit_all(ast)

    type_checker = MatrixTypeChecker()
    type_checker.visit_all(ast)

    # print(ast)

    print_errors_and_warnings()
