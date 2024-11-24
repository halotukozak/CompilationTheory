from typing import Tuple

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
        self.visit(if_.condition)
        if not isinstance(if_.condition.type, TS.Bool):
            report_error(self, f"Expected Bool, got {if_.condition.type}", if_.condition.lineno)
        self.visit_all(if_.then)
        if if_.else_:
            self.visit_all(if_.else_)

    def visit_While(self, while_: While):
        self.visit(while_.condition)
        if not isinstance(while_.condition.type, TS.Bool):
            report_error(self, f"Expected Bool, got {while_.condition.type}", while_.condition.lineno)
        self.visit_all(while_.body)

    def visit_For(self, for_: For):
        self.visit(for_.range)
        self.visit(for_.var)
        if not isinstance(for_.var.type, TS.Int):
            report_error(self, f"Expected Int, got {for_.var.type}", for_.var.lineno)
        self.visit_all(for_.body)

    def visit_Break(self, break_: Break):
        pass

    def visit_Continue(self, continue_: Continue):
        pass

    def visit_SymbolRef(self, ref: SymbolRef):
        pass

    def visit_MatrixRef(self, ref: MatrixRef):
        if not isinstance(ref.matrix.type, TS.Matrix):
            report_error(self, f"Expected Matrix, got {ref.matrix.type}", ref.lineno)

    def visit_VectorRef(self, ref: VectorRef):
        if not isinstance(ref.vector.type, TS.Vector):
            report_error(self, f"Expected Vector, got {ref.vector.type}", ref.lineno)

    def visit_Assign(self, assign: Assign):
        self.visit(assign.expr)
        assign.var.type = assign.expr.type

    def visit_Apply(self, apply: Apply):
        ref_type = apply.ref.type
        if isinstance(ref_type, TS.Function):
            if ref_type.args is None:
                if apply.args:
                    report_error(self, f"Expected 0 arguments, got {len(apply.args)}", apply.lineno)
            elif isinstance(ref_type.args, TS.VarArg):
                expected_type = ref_type.args.type
                for arg in apply.args:
                    if arg.type != expected_type:
                        report_error(self, f"Expected {expected_type}, got {arg.type}", apply.lineno)
            elif isinstance(ref_type.args, TS.Type):
                if len(apply.args) != 1:
                    report_error(self, f"Expected 1 argument, got {len(apply.args)}", apply.lineno)
                if apply.args[0].type != ref_type.args:
                    report_error(self, f"Expected {ref_type.args}, got {apply.args[0].type}", apply.lineno)
            elif isinstance(ref_type.args, Tuple):
                if len(apply.args) != len(ref_type.args):
                    report_error(self, f"Expected {len(ref_type.args)} arguments, got {len(apply.args)}", apply.lineno)
                for arg, expected_type in zip(apply.args, ref_type.args):
                    if arg.type != expected_type:
                        report_error(self, f"Expected {expected_type}, got {arg.type}", apply.lineno)
        elif isinstance(apply, TS.undef):
            report_error(self, f"Undefined function {apply.ref.name}", apply.lineno)
        elif isinstance(apply.type, TS.undef):
            pass  # error already reported
        else:
            raise NotImplementedError

    def visit_Range(self, range_: Range):
        self.visit(range_.start)
        self.visit(range_.end)
        if not isinstance(range_.start.type, TS.Int):
            report_error(self, f"Expected Int, got {range_.start.type}", range_.start.lineno)
        if not isinstance(range_.end.type, TS.Int):
            report_error(self, f"Expected Int, got {range_.end.type}", range_.end.lineno)

    def visit_Literal(self, literal: Literal):
        pass

    def visit_Return(self, return_: Return):
        pass
