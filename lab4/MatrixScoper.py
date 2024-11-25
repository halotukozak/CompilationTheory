from lab4 import AST, Predef
from lab4.AST import *
from lab4.SymbolTable import SymbolTable
from lab4.TypeSystem import AnyOf
from lab4.Utils import report_error, report_warn


class MatrixScoper:
    symbol_table = SymbolTable()

    def add_to_current_scope(self, symbol: SymbolRef) -> None:
        existing_symbol = self.get_symbol(symbol.name)
        if existing_symbol is not None and existing_symbol.type != symbol.type:
            report_warn(self,
                        f"Redeclaration of {symbol.name} : {existing_symbol.type} with new {symbol.type} type.",
                        symbol.lineno,
                        )
        scope = self.symbol_table.actual_scope
        scope.symbols[symbol.name] = symbol

    def create_scope(self, tree: AST.Tree, in_loop: Optional[bool] = None):
        key = id(tree)
        new_scope = self.symbol_table.Scope(self.symbol_table.actual_scope, key, in_loop)
        self.symbol_table.actual_scope.children[key] = new_scope
        self.symbol_table.push_scope(tree)

    def get_symbol(self, name: str) -> Optional[SymbolRef]:
        return self.symbol_table.get_symbol(name)

    def pop_scope(self):
        self.symbol_table.pop_scope()

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    @staticmethod
    def generic_visit(node):
        print(f"MatrixScoper: No visit_{node.__class__.__name__} method")

    def visit_all(self, tree: list[Statement]):
        for node in tree:
            self.visit(node)

    def visit_If(self, if_: If):
        self.visit(if_.condition)
        self.create_scope(if_.then)
        self.visit(if_.then)
        self.pop_scope()
        if if_.else_:
            self.create_scope(if_.else_)
            self.visit(if_.else_)
            self.pop_scope()

    def visit_While(self, while_: While):
        self.visit(while_.condition)
        self.create_scope(while_.body, in_loop=True)
        self.visit(while_.body)
        self.pop_scope()

    def visit_For(self, for_: For):
        self.visit(for_.range)
        self.create_scope(for_.body, in_loop=True)
        self.add_to_current_scope(for_.var)
        self.visit(for_.body)
        self.pop_scope()

    def visit_Break(self, break_: Break):
        if not self.symbol_table.actual_scope.in_loop:
            report_error(self, "Break outside loop", break_.lineno)

    def visit_Continue(self, continue_: Continue):
        if not self.symbol_table.actual_scope.in_loop:
            report_error(self, "Continue outside loop", continue_.lineno)

    def visit_SymbolRef(self, ref: SymbolRef):
        symbol = self.get_symbol(ref.name)
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
        if isinstance(assign.var, SymbolRef):
            assign.var.type = assign.expr.type
            symbol = self.get_symbol(assign.var.name)
            if symbol is None:
                self.add_to_current_scope(assign.var)
            else:
                symbol.type = assign.var.type

    def visit_Apply(self, apply: Apply):
        self.visit(apply.ref)
        self.visit_all(apply.args)
        arg_types = [arg.type for arg in apply.args]

        if not isinstance(apply.ref, SymbolRef):
            raise NotImplementedError
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
                apply.type = TS.undef()
            else:
                if not apply.ref.type.result.is_final:
                    self.visit_predef_apply(apply)
                assert isinstance(apply.ref.type, TS.Function)
                apply.type = apply.ref.type.result
        elif isinstance(apply.ref.type, TS.Function):
            if not apply.ref.type.takes(arg_types):
                apply.type = TS.undef()
            else:
                if not apply.ref.type.result.is_final:
                    self.visit_predef_apply(apply)
                apply.type = apply.ref.type.result
        else:
            raise NotImplementedError

    def visit_Range(self, range_: Range):
        self.visit(range_.start)
        self.visit(range_.end)
        if isinstance(range_.start, SymbolRef) and range_.start.type != TS.Int():
            raise NotImplementedError
        if isinstance(range_.end, SymbolRef) and range_.end.type != TS.Int():
            raise NotImplementedError

    def visit_Literal(self, literal: Literal):
        pass

    def visit_Return(self, return_: Return):
        self.visit(return_.expr)

    def visit_Block(self, block: Block):
        self.visit_all(block.statements)

    # todo: refactor
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
