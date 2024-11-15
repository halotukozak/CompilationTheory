from typing import Optional

from lab4.AST import *


class MatrixScoper:
    def __init__(self, errors):
        self.errors = errors

    class SymbolTable(object):
        operators = [
            # relation operators
            "<", ">", "<=", ">=", "!=", "==",
            # binary operators
            "+", "-", "*", '/',
            # matrix binary operators
            ".+", ".-", ".*", "./",
        ]
        assignment_operators = [
            "+=", "-=", "*=", "/="
        ]

        predefined_functions = [
            "eye", "zeros", "ones", "print"
        ]

        class Scope(object):
            symbols = {}

            def __init__(self, parent, name: str, in_loop: Optional[bool]):
                self.parent = parent  # :Scope
                self.name = name
                if in_loop is not None:
                    self.in_loop = in_loop
                else:
                    self.in_loop = parent.in_loop

            def put(self, name, symbol):
                self.symbols[name] = symbol

            def get(self, name):
                if name in self.symbols:
                    return self.symbols[name]
                return self.parent.get(name) if self.parent else None

        global_functions = operators + assignment_operators + predefined_functions

        global_scope = Scope(None, "global", False)
        global_scope.symbols = {name: None for name in global_functions}

        actual_scope = global_scope

        def get(self, name):
            return self.actual_scope.get(name)

        def addToCurrentScope(self, name, symbol):
            self.actual_scope.put(name, symbol)

        def pushScope(self, name, in_loop: Optional[bool] = None):
            self.actual_scope = self.Scope(self.actual_scope, name, in_loop)

        def popScope(self):
            self.actual_scope = self.actual_scope.parent

    symbol_table = SymbolTable()

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        pass

    def visit_all(self, tree: list[Statement]):
        for node in tree:
            self.visit(node)

    def visit_If(self, if_: If):
        self.symbol_table.pushScope("if")
        self.visit_all(if_.then)
        self.symbol_table.popScope()
        if if_.else_:
            self.symbol_table.pushScope("else")
            self.visit_all(if_.else_)
            self.symbol_table.popScope()

    def visit_While(self, while_: While):
        self.symbol_table.pushScope("while", in_loop=True)
        self.visit(while_.condition)
        self.visit_all(while_.body)
        self.symbol_table.popScope()

    def visit_For(self, for_: For):
        self.symbol_table.pushScope("for", in_loop=True)
        self.visit_all(for_.body)
        self.symbol_table.popScope()

    def visit_Break(self, break_: Break):
        if not self.symbol_table.actual_scope.in_loop:
            self.errors[break_.lineno].append("Break outside loop")

    def visit_Continue(self, continue_: Continue):
        if not self.symbol_table.actual_scope.in_loop:
            self.errors[continue_.lineno].append("Continue outside loop")

    def visit_SymbolRef(self, ref: SymbolRef):
        if self.symbol_table.get(ref.name) is None:
            self.errors[ref.lineno].append(f"Undefined variable {ref.name}")

    def visit_Assign(self, assign: Assign):
        self.visit(assign.expr)
        self.symbol_table.addToCurrentScope(assign.var.name, assign)
