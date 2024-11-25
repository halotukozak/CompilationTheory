import sys

from lab4.MatrixParser import MatrixParser
from lab4.MatrixScanner import MatrixScanner
from lab4.MatrixScoper import MatrixScoper
from lab4.MatrixTypeChecker import MatrixTypeChecker
from lab4.MatrixTypeInterferer import MatrixTypeInterferer
from lab4.SymbolTable import SymbolTable
from lab4.Utils import errors_and_warnings

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

    symbol_table = SymbolTable()

    scoper = MatrixScoper(symbol_table)
    scoper.visit_all(ast)

    type_interferer = MatrixTypeInterferer(symbol_table)
    type_interferer.visit_all(ast)

    type_checker = MatrixTypeChecker()
    type_checker.visit_all(ast)

    print(ast)

    for i, line in sorted(errors_and_warnings.items()):
        tab = "  " if i < 10 else " " if i < 100 else ""
        print(f"Line {tab}{i}:")
        for level, msg in line:
            print(f"\t{level}: {msg}")
