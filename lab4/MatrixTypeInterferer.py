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
        self.visit(assign.var)
        self.visit(assign.expr)
        if isinstance(assign.var, SymbolRef):
            assign.var.type = assign.expr.type
            symbol = self.get_symbol(assign.var.name)
            if symbol is not None:
                symbol.type = assign.var.type

    def visit_Apply(self, apply: Apply):
        self.visit(apply.ref)
        self.visit_all(apply.args)
        arg_types = [arg.type for arg in apply.args]

        assert isinstance(apply.ref, SymbolRef)
        ref_name = apply.ref.name

        if ref_name == 'INIT':  # or compare symbols?
            if all(arg == TS.numerical for arg in arg_types):
                vector_symbol = Predef.get_symbol("INIT_VECTOR")(len(apply.args))
                assert isinstance(vector_symbol.type, TS.Function)
                apply.ref = vector_symbol
                apply.type = vector_symbol.type.result
            elif all(arg == TS.Vector() for arg in arg_types):
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
        elif isinstance(apply.ref.type, AnyOf):
            apply.ref.type = next(
                (type_ for type_ in apply.ref.type.all if
                 isinstance(type_, TS.Function) and type_.takes(arg_types)),
                TS.undef()
            )
            if isinstance(apply.ref.type, TS.undef):
                # todo:hint possible cases?
                report_error(self, f"Function {ref_name} does not take {arg_types} arguments", apply.lineno)
                apply.type = TS.undef()
            else:
                if not apply.ref.type.result.is_final:
                    self.visit_predef_apply(apply)
                assert isinstance(apply.ref.type, TS.Function)
                apply.type = apply.ref.type.result
        elif isinstance(apply.ref.type, TS.Function):
            if not apply.ref.type.takes(arg_types):
                report_error(self, f"Function {ref_name} does not take {arg_types} arguments", apply.lineno)
                apply.type = TS.undef()
            else:
                if not apply.ref.type.result.is_final:
                    self.visit_predef_apply(apply)
                apply.type = apply.ref.type.result
        else:
            raise NotImplementedError

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

    def visit_predef_apply(self, apply: Apply):
        assert isinstance(apply.ref, SymbolRef)
        ref_name = apply.ref.name
        arg_types = [arg.type for arg in apply.args]
        match ref_name:
            case "ones" | "zeros" | "eye":
                arg = apply.args[0]
                assert isinstance(arg, Literal)
                assert isinstance(arg.value, int)
                apply.ref = Predef.get_symbol(f"{ref_name}_Matrix")(arg.value)
            case '+' | '-':
                a, b = arg_types

                if isinstance(a, TS.Vector) and isinstance(b, TS.Vector):
                    if a.arity == b.arity:
                        apply.ref = Predef.get_symbol("BINARY_Vector")(a.arity, ref_name)
                    else:
                        report_error(self, f"Vector arities {a.arity} and {b.arity} are not the same", apply.lineno)
                        apply.ref = Predef.get_symbol("BINARY_Vector")(None, ref_name)
                elif isinstance(a, TS.Matrix) and isinstance(b, TS.Matrix):
                    if a.arity == b.arity:
                        apply.ref = Predef.get_symbol("BINARY_Matrix")(*a.arity, ref_name)
                    else:
                        report_error(self, f"Matrix arities {a.arity} and {b.arity} are not the same", apply.lineno)
                        apply.ref = Predef.get_symbol("BINARY_Matrix")(None, None, ref_name)
                else:
                    raise NotImplementedError
            case '*':
                a, b = arg_types

                if isinstance(a, TS.Matrix) and isinstance(b, TS.Matrix):
                    if a.arity == b.arity:
                        apply.ref = Predef.get_symbol("BINARY_Matrix")(*a.arity, ref_name)
                    else:
                        report_error(self, f"Matrix arities {a.arity} and {b.arity} are not the same", apply.lineno)
                        apply.ref = Predef.get_symbol("BINARY_Matrix")(None, None, ref_name)
                elif isinstance(a, TS.Vector) and b == TS.numerical:
                    apply.ref = Predef.get_symbol("SCALAR_Vector")(a.arity, ref_name)
                elif isinstance(a, TS.Matrix) and b == TS.numerical:
                    apply.ref = Predef.get_symbol("SCALAR_Matrix")(*a.arity, ref_name)
                else:
                    raise NotImplementedError
            case '/' | '.+' | '.-' | '.*' | './':
                a, b = arg_types

                if isinstance(a, TS.Vector) and b == TS.numerical:
                    apply.ref = Predef.get_symbol("SCALAR_Vector")(a.arity, ref_name)
                elif isinstance(a, TS.Matrix) and b == TS.numerical:
                    apply.ref = Predef.get_symbol("SCALAR_Matrix")(*a.arity, ref_name)
                else:
                    raise NotImplementedError
            case "'":
                a = arg_types[0]
                assert isinstance(a, TS.Matrix)
                apply.ref = Predef.get_symbol("'_Matrix")(*a.arity, ref_name)
            case 'UMINUS':
                a = arg_types[0]
                if isinstance(a, TS.Vector):
                    apply.ref = Predef.get_symbol("-_Vector")(a.arity, ref_name)
                elif isinstance(a, TS.Matrix):
                    apply.ref = Predef.get_symbol("-_Matrix")(*a.arity, ref_name)
                else:
                    raise NotImplementedError
            case _:
                raise NotImplementedError
