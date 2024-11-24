import TypeSystem
from TypeSystem import *
from lab4.AST import *
from lab4.Utils import report_error


class MatrixTypeChecker:

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        print(f"No visit_{node.__class__.__name__} method")

    def visit_all(self, tree: list[Statement]):
        for node in tree:
            self.visit(node)

    def visit_If(self, if_: If):
        raise NotImplementedError

    def visit_While(self, while_: While):
        raise NotImplementedError

    def visit_For(self, for_: For):
        raise NotImplementedError

    def visit_Break(self, break_: Break):
        raise NotImplementedError

    def visit_Continue(self, continue_: Continue):
        raise NotImplementedError

    def visit_SymbolRef(self, ref: SymbolRef):
        raise NotImplementedError

    def visit_MatrixRef(self, ref: MatrixRef):
        assert ref.matrix.type == TypeSystem.Matrix

    def visit_VectorRef(self, ref: VectorRef):
        assert ref.vector.type == TypeSystem.Vector

    def visit_Assign(self, assign: Assign):
        self.visit(assign.expr)
        assign.var.type = assign.expr.type

    def visit_Apply(self, apply: Apply):
        if isinstance(apply.fun.type, Function):  # todo: can be checked arity here?
            report_error(self, f"Expected function, got {apply.fun.type}", apply.lineno)
        elif apply.fun.type == TypeSystem.undef and apply.fun.type.arity != len(apply.args):
            report_error(self, f"Expected {apply.fun.type.arity} arguments, got {len(apply.args)}", apply.lineno)
        else:
            pass

    def visit_Range(self, range_: Range):
        raise NotImplementedError

    def visit_Literal(self, literal: Literal):
        pass

    def visit_Return(self, return_: Return):
        raise NotImplementedError
