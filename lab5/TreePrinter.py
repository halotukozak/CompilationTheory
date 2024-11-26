from lab5.AST import *
from lab5.Utils import addToClass


class TreePrinter:
    @staticmethod
    def safe_print_tree(obj, indent_level):
        """Helper function to handle primitives and objects with `print_tree`."""
        prefix = "|  " * indent_level
        if obj is not None:
            obj.print_tree(indent_level)
        else:
            print(f"{prefix}None")

    @addToClass(Assign)
    def print_tree(self: Assign, indent_level=0):
        print("|  " * indent_level + "=")
        TreePrinter.safe_print_tree(self.var, indent_level + 1)
        TreePrinter.safe_print_tree(self.expr, indent_level + 1)

    @addToClass(If)
    def print_tree(self: If, indent_level=0):
        print("|  " * indent_level + "IF")
        TreePrinter.safe_print_tree(self.condition, indent_level + 1)
        print("|  " * indent_level + "THEN")
        for stmt in self.then:
            stmt.print_tree(indent_level + 1)
        if self.else_:
            print("|  " * indent_level + "ELSE")
            for stmt in self.else_:
                stmt.print_tree(indent_level + 1)

    @addToClass(While)
    def print_tree(self: While, indent_level=0):
        print("|  " * indent_level + "WHILE")
        print("|  " * (indent_level + 1) + "CONDITION")
        TreePrinter.safe_print_tree(self.condition, indent_level + 2)
        print("|  " * (indent_level + 1) + "BODY")
        for stmt in self.body:
            stmt.print_tree(indent_level + 2)

    @addToClass(For)
    def print_tree(self: For, indent_level=0):
        print("|  " * indent_level + "FOR")
        print("|  " * (indent_level + 1) + self.var.name)
        print("|  " * (indent_level + 1) + "RANGE")
        TreePrinter.safe_print_tree(self.range.start, indent_level + 2)
        TreePrinter.safe_print_tree(self.range.end, indent_level + 2)
        print("|  " * (indent_level + 1) + "BODY")
        for stmt in self.body:
            stmt.print_tree(indent_level + 2)

    @addToClass(Apply)
    def print_tree(self: Apply, indent_level=0):
        print("|  " * indent_level + f"{self.ref.name}")
        print("|  " * (indent_level + 1) + "ARGUMENTS")
        for arg in self.args:
            TreePrinter.safe_print_tree(arg, indent_level + 2)

    @addToClass(Range)
    def print_tree(self: Range, indent_level=0):
        print("|  " * indent_level + "RANGE")
        TreePrinter.safe_print_tree(self.start, indent_level + 1)
        TreePrinter.safe_print_tree(self.end, indent_level + 1)

    @addToClass(SymbolRef)
    def print_tree(self: SymbolRef, indent_level=0):
        print("|  " * indent_level + self.name)

    @addToClass(VectorRef)
    def print_tree(self: VectorRef, indent_level=0):
        print("|  " * indent_level + "VECTORREF")
        print("|  " * (indent_level + 1) + "ARGUMENTS")
        TreePrinter.safe_print_tree(self.vector, indent_level + 2)
        TreePrinter.safe_print_tree(self.element, indent_level + 2)

    @addToClass(MatrixRef)
    def print_tree(self: MatrixRef, indent_level=0):
        print("|  " * indent_level + "MATRIXREF")
        print("|  " * (indent_level + 1) + "ARGUMENTS")
        TreePrinter.safe_print_tree(self.matrix, indent_level + 2)
        TreePrinter.safe_print_tree(self.row, indent_level + 2)
        TreePrinter.safe_print_tree(self.col, indent_level + 2)

    @addToClass(Literal)
    def print_tree(self: Literal, indent_level=0):
        print("|  " * indent_level + str(self.value))

    @addToClass(Break)
    def print_tree(self: Break, indent_level=0):
        print("|  " * indent_level + "BREAK")

    @addToClass(Continue)
    def print_tree(self: Continue, indent_level=0):
        print("|  " * indent_level + "CONTINUE")

    @addToClass(Return)
    def print_tree(self: Return, indent_level=0):
        print("|  " * indent_level + "RETURN")
        TreePrinter.safe_print_tree(self.expr, indent_level + 1)

    def print_result(self, result):
        for r in result:
            r.print_tree()
