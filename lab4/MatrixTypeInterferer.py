from lab4 import Predef
from lab4.AST import *
from lab4.SymbolTable import SymbolTable
from lab4.TypeSystem import AnyOf
from lab4.Utils import report_error


# if assert fails, sth has not been implemented

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

        assert isinstance(apply.ref, SymbolRef)

        ref_name = apply.ref.name

        if ref_name == "INIT":  # or compare symbols?
            self.visit_init(apply)
        elif isinstance(apply.ref.type, AnyOf):
            res = next(
                (type_ for type_ in apply.ref.type.all if
                 isinstance(type_, TS.Function) and type_.takes(arg_types)),
                TS.undef()
            )
            if isinstance(res, TS.undef):
                # todo:hint possible cases?
                report_error(self, f"Function {ref_name} with arguments {arg_types} not found", apply.lineno)
                apply.ref.type = TS.undef()
                apply.type = TS.undef()
            else:
                assert isinstance(res, TS.Function)
                self.visit_predef_apply(apply)
                apply.ref.type = res
                apply.type = res.result
        elif isinstance(apply.ref.type, TS.Function):
            if not apply.ref.type.takes(arg_types):
                report_error(self, f"Function {ref_name} with arguments {arg_types} not found", apply.lineno)
                apply.type = TS.undef()
            else:
                self.visit_predef_apply(apply)
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

    #     Helpers

    def visit_init(self, apply: Apply):
        assert isinstance(apply.ref, SymbolRef)

        if all(isinstance(arg, Literal) for arg in apply.args):
            vector_symbol = Predef.get_symbol("INIT_VECTOR")(len(apply.args))
            assert isinstance(vector_symbol.type, TS.Function)
            apply.ref = vector_symbol
            apply.type = vector_symbol.type.result
        elif all(isinstance(arg.type, TS.Vector) for arg in apply.args):
            for arg in apply.args:
                assert isinstance(arg.type, TS.Vector)
            arities = [arg.type.arity for arg in apply.args]
            if all(arity == arities[0] for arity in arities):  # all arities are the same
                matrix_symbol = Predef.get_symbol("INIT_MATRIX")(arities[0], len(apply.args))
                assert isinstance(matrix_symbol.type, TS.Function)
                apply.ref = matrix_symbol
                apply.type = matrix_symbol.type.result
            else:
                report_error(self, f"Vector arities {arities} are not the same", apply.lineno)
                apply.ref = Predef.get_symbol("INIT_MATRIX")(None, len(apply.args))
                apply.type = TS.Matrix()
        else:
            raise NotImplementedError

    def visit_predef_apply(self, apply: Apply):
        assert isinstance(apply.ref, SymbolRef)
        ref_name = apply.ref.name
        arg_types = [arg.type for arg in apply.args]
        match ref_name:
            case "ones" | "zeros" | "eye":
                assert len(apply.args) == 1
                arg = apply.args[0]
                assert isinstance(arg, Literal)
                assert isinstance(arg.value, int)
                symbol = Predef.get_symbol(f"{ref_name}_Matrix")(arg.value)
                assert isinstance(symbol.type, TS.Function)
                apply.ref = symbol
                apply.type = symbol.type.result
            case '+':
                assert len(arg_types) == 2
                a, b = arg_types

                if a == TS.Int() and b == TS.Int():
                    apply.type = TS.Int()
                elif a == TS.numerical and b == TS.numerical:
                    apply.type = TS.Float()
                elif isinstance(a, TS.Vector) and isinstance(b, TS.Vector):
                    apply.type = TS.Vector()
                elif isinstance(a, TS.Matrix) and isinstance(b, TS.Matrix):
                    if a.arity == b.arity:
                        symbol = Predef.get_symbol("BINARY_Matrix")(*a.arity, ref_name)
                    else:
                        report_error(self, f"Matrix arities {a.arity} and {b.arity} are not the same", apply.lineno)
                        symbol = Predef.get_symbol("BINARY_Matrix")(None, None, ref_name)
                    apply.ref = symbol
                    assert isinstance(symbol.type, TS.Function)
                    apply.type = symbol.type.result
                else:
                    raise NotImplementedError
            case '*':
                assert len(arg_types) == 2
                a, b = arg_types

                if a == TS.Int() and b == TS.Int():
                    apply.type = TS.Int()
                elif a == TS.numerical and b == TS.numerical:
                    apply.type = TS.Float()
                elif isinstance(a, TS.Vector) and isinstance(b, TS.Vector):
                    apply.type = TS.Vector()
                elif isinstance(a, TS.Matrix) and isinstance(b, TS.Matrix):
                    if a.arity == b.arity:
                        symbol = Predef.get_symbol("BINARY_Matrix")(*a.arity, ref_name)
                    else:
                        report_error(self, f"Matrix arities {a.arity} and {b.arity} are not the same", apply.lineno)
                        symbol = Predef.get_symbol("BINARY_Matrix")(None, None, ref_name)
                    apply.ref = symbol
                    assert isinstance(symbol.type, TS.Function)
                    apply.type = symbol.type.result
                elif isinstance(a, TS.Vector) and b == TS.numerical:
                    symbol = Predef.get_symbol("*_Vector")(a.arity, ref_name)
                    apply.ref = symbol
                    assert isinstance(symbol.type, TS.Function)
                    apply.type = symbol.type.result
                elif isinstance(a, TS.Matrix) and b == TS.numerical:
                    symbol = Predef.get_symbol("*_Matrix")(*a.arity, ref_name)
                    apply.ref = symbol
                    assert isinstance(symbol.type, TS.Function)
                    apply.type = symbol.type.result
                else:
                    raise NotImplementedError
            case '.+' | '.-' | '.*' | './':
                assert len(arg_types) == 2
                a, b = arg_types

                if isinstance(a, TS.Vector) and isinstance(b, TS.numerical):
                    symbol = Predef.get_symbol("SCALAR_Vector")(a.arity, ref_name)
                    apply.ref = symbol
                    assert isinstance(symbol.type, TS.Function)
                    apply.type = symbol.type.result
                elif isinstance(a, TS.Matrix) and isinstance(b, TS.Matrix):
                    symbol = Predef.get_symbol("SCALAR_Matrix")(*a.arity, ref_name)
                    apply.ref = symbol
                    assert isinstance(symbol.type, TS.Function)
                    apply.type = symbol.type.result
                else:
                    raise NotImplementedError
            case "'":
                assert len(arg_types) == 1
                a = arg_types[0]
                if isinstance(a, TS.Matrix):
                    symbol = Predef.get_symbol("'_Matrix")(*a.arity, ref_name)
                    apply.ref = symbol
                    assert isinstance(symbol.type, TS.Function)
                    apply.type = symbol.type.result
                else:
                    raise NotImplementedError
            case _:
                raise NotImplementedError
