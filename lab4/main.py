import sys
from collections import defaultdict

from lab4.MatrixParser import MatrixParser
from lab4.MatrixScanner import MatrixScanner
from lab4.MatrixScoper import MatrixScoper

if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) > 1 else "examples/scopes.m"
    try:
        file = open(filename, "r")
    except IOError:
        print(f"Cannot open {filename} file")
        sys.exit(0)

    text = file.read()
    lexer = MatrixScanner()
    parser = MatrixParser()

    result = parser.parse(lexer.tokenize(text))
    # print(result)
    # treePrinter = TreePrinter()
    # treePrinter.printResult(result)

    if result is None:
        sys.exit(1)

    errors = defaultdict(list)
    scoper = MatrixScoper(errors)
    scoper.visit_all(result)

    for lineno, error in errors.items():
        for e in error:
            print(f"Error at line {lineno}: {e}")
