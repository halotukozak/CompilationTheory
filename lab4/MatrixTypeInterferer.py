from lab4 import Predef
from lab4.AST import *
from lab4.SymbolTable import SymbolTable
from lab4.TypeSystem import AnyOf
from lab4.Utils import report_error


class MatrixTypeInterferer:

    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table

    def get_symbol(self, name: str) -> Optional[SymbolRef]:
        return self.symbol_table.get_symbol(name)

    def pop_scope(self):
        self.symbol_table.pop_scope()

    def push_scope(self, name: Any):
        self.symbol_table.push_scope(name)

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    @staticmethod
    def generic_visit(node):
        print(f"MatrixTypeInterferer: No visit_{node.__class__.__name__} method")

    def visit_all(self, tree: list[Statement]):
        for node in tree:
            self.visit(node)

    def visit_If(self, if_: If):
        self.visit(if_.condition)
        self.push_scope(if_.then)
        self.visit(if_.then)
        self.pop_scope()
        if if_.else_:
            self.push_scope(if_.else_)
            self.visit(if_.else_)
            self.pop_scope()

    def visit_While(self, while_: While):
        self.visit(while_.condition)
        self.push_scope(while_.body)
        self.visit(while_.body)
        self.pop_scope()

    def visit_For(self, for_: For):
        self.visit(for_.range)
        self.push_scope(for_.body)
        self.visit(for_.body)
        self.pop_scope()

    def visit_Break(self, break_: Break):
        pass

    def visit_Continue(self, continue_: Continue):
        pass

    def visit_SymbolRef(self, ref: SymbolRef):
        symbol = self.get_symbol(ref.name)
        if symbol is not None:
            ref.type = symbol.type

    def visit_MatrixRef(self, ref: MatrixRef):
        self.visit(ref.matrix)

    def visit_VectorRef(self, ref: VectorRef):
        self.visit(ref.vector)

    def visit_Assign(self, assign: Assign):
        self.visit(assign.expr)
        assign.var.type = assign.expr.type
        if isinstance(assign.var, SymbolRef):
            symbol = self.get_symbol(assign.var.name)
            if symbol is not None:
                symbol.type = assign.var.type
        else:
            raise NotImplementedError

    def visit_Apply(self, apply: Apply):
        self.visit(apply.ref)
        self.visit_all(apply.args)
        arg_types = [arg.type for arg in apply.args]
        if apply.ref == Predef.get_symbol("INIT"):  # or compare name
            if all(isinstance(arg, Literal) for arg in apply.args):
                vector_symbol = Predef.get_symbol("INIT_VECTOR")(len(apply.args))
                apply.ref = vector_symbol
                apply.type = vector_symbol.type.result
            elif all(isinstance(arg.type, TS.Vector) for arg in apply.args):
                arities = [arg.type.arity for arg in apply.args]
                if all(arity == arities[0] for arity in arities):  # all arities are the same
                    matrix_symbol = Predef.get_symbol("INIT_MATRIX")(arities[0], len(apply.args))
                    apply.ref = matrix_symbol
                    apply.type = matrix_symbol.type.result
                else:
                    report_error(self, f"Vector arities {arities} are not the same", apply.lineno)
                    apply.ref = Predef.get_symbol("INIT_MATRIX")(None, len(apply.args))
                    apply.type = TS.Matrix()
            else:
                raise NotImplementedError
        elif isinstance(apply.ref.type, AnyOf):
            res = next(
                (type_ for type_ in apply.ref.type.all if isinstance(type_, TS.Function) and type_.takes(arg_types)),
                TS.undef()
            )
            if isinstance(res, TS.undef):
                report_error(self, f"Function {apply.ref.name} with arguments {arg_types} not found", apply.lineno)
                apply.ref.type = TS.undef()
                apply.type = TS.undef()
            else:
                apply.ref.type = res
                apply.type = res.result
        elif isinstance(apply.ref.type, TS.Function):
            apply.type = apply.ref.type.result
        else:
            pass

    def visit_Range(self, range_: Range):
        self.visit(range_.start)
        if isinstance(range_.start, SymbolRef) and range_.start.type != TS.Int():
            range_.start.type = TS.Int()
        self.visit(range_.end)

    def visit_Literal(self, literal: Literal):
        pass

    def visit_Return(self, return_: Return):
        self.visit(return_.expr)

    def visit_Block(self, block: Block):
        self.visit_all(block.statements)
