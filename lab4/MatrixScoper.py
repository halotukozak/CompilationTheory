from lab4 import Predef
from lab4.AST import *
from lab4.TypeSystem import AnyOf
from lab4.Utils import report_error


class MatrixScoper:
    # todo: for now, we only persist types
    class SymbolTable(object):

        class Scope(object):
            symbols = {}

            def __init__(self, parent, name: str, in_loop: Optional[bool]):
                self.parent = parent  # :Scope
                self.name = name
                if in_loop is not None:
                    self.in_loop = in_loop
                else:
                    self.in_loop = parent.in_loop

            def put(self, name: str, symbol: SymbolRef):
                self.symbols[name] = symbol

            def get(self, name: str) -> Optional[SymbolRef]:
                if name in self.symbols.keys():
                    return self.symbols[name]
                return self.parent.get(name) if self.parent else None

            def __contains__(self, symbol: SymbolRef) -> bool:
                return symbol.name in self.symbols.keys() or (self.parent is not None and symbol in self.parent)

        global_scope = Scope(None, "global", False)
        global_scope.symbols = Predef.symbols

        actual_scope = global_scope

        def get(self, name: str) -> Optional[SymbolRef]:
            return self.actual_scope.get(name)

        def add_to_current_scope(self, symbol: SymbolRef) -> None:
            if symbol in self.actual_scope:
                report_error(self, f"Variable {symbol.name} already defined", symbol.lineno)
            self.actual_scope.put(symbol.name, symbol)

        def push_scope(self, name, in_loop: Optional[bool] = None):
            self.actual_scope = self.Scope(self.actual_scope, name, in_loop)

        def pop_scope(self):
            self.actual_scope = self.actual_scope.parent

    symbol_table = SymbolTable()

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    @staticmethod
    def generic_visit(node):
        print(f"No visit_{node.__class__.__name__} method")

    def visit_all(self, tree: list[Statement]):
        for node in tree:
            self.visit(node)

    def visit_If(self, if_: If):
        self.symbol_table.push_scope("if")
        self.visit(if_.condition)
        self.visit_all(if_.then)
        self.symbol_table.pop_scope()
        if if_.else_:
            self.symbol_table.push_scope("else")
            self.visit_all(if_.else_)
            self.symbol_table.pop_scope()

    def visit_While(self, while_: While):
        self.symbol_table.push_scope("while", in_loop=True)
        self.visit(while_.condition)
        self.visit_all(while_.body)
        self.symbol_table.pop_scope()

    def visit_For(self, for_: For):
        self.symbol_table.push_scope("for", in_loop=True)
        self.visit(for_.range)
        self.symbol_table.add_to_current_scope(for_.var)
        self.visit_all(for_.body)
        self.symbol_table.pop_scope()

    def visit_Break(self, break_: Break):
        if not self.symbol_table.actual_scope.in_loop:
            report_error(self, "Break outside loop", break_.lineno)

    def visit_Continue(self, continue_: Continue):
        if not self.symbol_table.actual_scope.in_loop:
            report_error(self, "Continue outside loop", continue_.lineno)

    def visit_SymbolRef(self, ref: SymbolRef):
        symbol = self.symbol_table.get(ref.name)
        if symbol is None:
            report_error(self, f"Undefined variable {ref.name}", ref.lineno)
        else:
            ref.type = symbol.type

    def visit_MatrixRef(self, ref: MatrixRef):
        self.visit(ref.matrix)

    def visit_VectorRef(self, ref: VectorRef):
        self.visit(ref.vector)

    def visit_Assign(self, assign: Assign):
        self.visit(assign.expr)
        assign.var.type = assign.expr.type
        if isinstance(assign.var, SymbolRef):
            symbol = self.symbol_table.get(assign.var.name)
            if symbol is None:
                self.symbol_table.add_to_current_scope(assign.var)
            else:
                symbol.type = assign.var.type
        else:
            raise NotImplementedError

    def visit_Apply(self, apply: Apply):
        self.visit(apply.ref)
        for arg in apply.args:
            self.visit(arg)
        arg_types = [arg.type for arg in apply.args]
        if isinstance(apply.ref.type, AnyOf):
            res = next(
                (type_ for type_ in apply.ref.type.all if isinstance(type_, TS.Function) and type_.takes(arg_types)),
                TS.undef()
            )
            if isinstance(res, TS.undef):
                report_error(self, f"Function {apply.ref.name} with arguments {arg_types} not found", apply.lineno)
                apply.type = TS.undef()
            else:
                apply.type = res.result
        elif isinstance(apply.ref.type, TS.Function):
            apply.type = apply.ref.type.result
        else:
            pass

    def visit_Range(self, range_: Range):
        self.visit(range_.start)
        self.visit(range_.end)

    def visit_Literal(self, literal: Literal):
        pass

    def visit_Return(self, return_: Return):
        self.visit(return_.expr)
