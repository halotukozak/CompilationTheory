import sys

from lab4.MatrixParser import MatrixParser
from lab4.MatrixScanner import MatrixScanner
from lab4.MatrixScoper import MatrixScoper

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
    result = parser.parse(tokens)
    quit_if_failed(parser)
    # print(result)
    # treePrinter = TreePrinter()
    # treePrinter.printResult(result)

    scoper = MatrixScoper()
    scoper.visit_all(result)
    quit_if_failed(scoper)
