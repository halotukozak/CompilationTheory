from lab3.AST import *


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
        if isinstance(obj, (int, float, str)):
            print(f"{prefix}{obj}")
        elif obj is not None:
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
        print("|  " * (indent_level + 1) + self.var.symbol)
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
        print("|  " * indent_level + self.symbol)

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
        TreePrinter.safePrintTree(self.matrix, indent_level + 1)
        print("|  " * (indent_level + 1) + f"ROW: {self.row}, COLUMN: {self.col}")

    def printResult(self, result):
        for r in result:
            r.printTree()
