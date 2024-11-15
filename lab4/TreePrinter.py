from lab4.AST import *


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


class TreePrinter:
    @staticmethod
    def safePrintTree(obj, indent_level):
        """Helper function to handle primitives and objects with `printTree`."""
        prefix = "|  " * indent_level
        if obj is not None:
            obj.printTree(indent_level)
        else:
            print(f"{prefix}None")

    @addToClass(Assign)
    def printTree(self: Assign, indent_level=0):
        print("|  " * indent_level + "=")
        TreePrinter.safePrintTree(self.var, indent_level + 1)
        TreePrinter.safePrintTree(self.expr, indent_level + 1)

    @addToClass(If)
    def printTree(self: If, indent_level=0):
        print("|  " * indent_level + "IF")
        TreePrinter.safePrintTree(self.condition, indent_level + 1)
        print("|  " * indent_level + "THEN")
        for stmt in self.then:
            stmt.printTree(indent_level + 1)
        if self.else_:
            print("|  " * indent_level + "ELSE")
            for stmt in self.else_:
                stmt.printTree(indent_level + 1)

    @addToClass(While)
    def printTree(self: While, indent_level=0):
        print("|  " * indent_level + "WHILE")
        print("|  " * (indent_level + 1) + "CONDITION")
        TreePrinter.safePrintTree(self.condition, indent_level + 2)
        print("|  " * (indent_level + 1) + "BODY")
        for stmt in self.body:
            stmt.printTree(indent_level + 2)

    @addToClass(For)
    def printTree(self: For, indent_level=0):
        print("|  " * indent_level + "FOR")
        print("|  " * (indent_level + 1) + self.var.name)
        print("|  " * (indent_level + 1) + "RANGE")
        TreePrinter.safePrintTree(self.range.start, indent_level + 2)
        TreePrinter.safePrintTree(self.range.end, indent_level + 2)
        print("|  " * (indent_level + 1) + "BODY")
        for stmt in self.body:
            stmt.printTree(indent_level + 2)

    @addToClass(Apply)
    def printTree(self: Apply, indent_level=0):
        print("|  " * indent_level + f"{self.fun.symbol.upper()}")
        print("|  " * (indent_level + 1) + "ARGUMENTS")
        for arg in self.args:
            TreePrinter.safePrintTree(arg, indent_level + 2)

    @addToClass(Range)
    def printTree(self: Range, indent_level=0):
        print("|  " * indent_level + "RANGE")
        TreePrinter.safePrintTree(self.start, indent_level + 1)
        TreePrinter.safePrintTree(self.end, indent_level + 1)

    @addToClass(SymbolRef)
    def printTree(self: SymbolRef, indent_level=0):
        print("|  " * indent_level + self.name)

    @addToClass(Vector)
    def printTree(self: Vector, indent_level=0):
        print("|  " * indent_level + "VECTOR")
        for elem in self.elements:
            TreePrinter.safePrintTree(elem, indent_level + 1)

    @addToClass(Matrix)
    def printTree(self: Matrix, indent_level=0):
        print("|  " * indent_level + "MATRIX")
        for vector in self.vectors:
            vector.printTree(indent_level + 1)

    @addToClass(MatrixRef)
    def printTree(self: MatrixRef, indent_level=0):
        print("|  " * indent_level + "MATRIXREF")
        print("|  " * (indent_level + 1) + "ARGUMENTS")
        TreePrinter.safePrintTree(self.matrix, indent_level + 2)
        TreePrinter.safePrintTree(self.row, indent_level + 2)
        TreePrinter.safePrintTree(self.col, indent_level + 2)

    @addToClass(Literal)
    def printTree(self: Literal, indent_level=0):
        print("|  " * indent_level + str(self.value))

    @addToClass(Break)
    def printTree(self: Break, indent_level=0):
        print("|  " * indent_level + "BREAK")

    @addToClass(Continue)
    def printTree(self: Continue, indent_level=0):
        print("|  " * indent_level + "CONTINUE")

    def printResult(self, result):
        for r in result:
            r.printTree()
