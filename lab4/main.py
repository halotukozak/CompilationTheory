import sys

from lab4.MatrixParser import MatrixParser
from lab4.MatrixScanner import MatrixScanner
from lab4.MatrixScoper import MatrixScoper
from lab4.MatrixTypeChecker import MatrixTypeChecker
from lab4.MatrixTypeInterferer import MatrixTypeInterferer
from lab4.SymbolTable import SymbolTable

if __name__ == '__main__':
    name = "examples/init.m"
    filename = sys.argv[1] if len(sys.argv) > 1 else name
    try:
        file = open(filename, "r")
    except IOError:
        print(f"Cannot open {filename} file")
        sys.exit(0)


    def quit_if_failed(self):
        if getattr(self, 'failed', False):
            sys.exit(0)


    text = file.read()
    lexer = MatrixScanner()
    tokens = lexer.tokenize(text)
    quit_if_failed(lexer)

    parser = MatrixParser()
    result = parser.parse(tokens)
    quit_if_failed(parser)
    # treePrinter = TreePrinter()
    # treePrinter.print_result(result)

    symbol_table = SymbolTable()

    scoper = MatrixScoper(symbol_table)
    scoper.visit_all(result)

    type_interferer = MatrixTypeInterferer(symbol_table)
    type_interferer.visit_all(result)

    type_checker = MatrixTypeChecker()
    type_checker.visit_all(result)
