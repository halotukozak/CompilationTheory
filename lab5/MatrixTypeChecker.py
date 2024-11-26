from lab5.AST import *
from lab5.Utils import report_error, report_warn


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
        self.visit(if_.then)
        if if_.else_:
            self.visit(if_.else_)

    def visit_While(self, while_: While):
        self.visit(while_.condition)
        if not isinstance(while_.condition.type, TS.Bool):
            report_error(self, f"Expected Bool, got {while_.condition.type}", while_.condition.lineno)
        self.visit(while_.body)

    def visit_For(self, for_: For):
        self.visit(for_.range)
        self.visit(for_.var)
        if not isinstance(for_.var.type, TS.Int):
            report_error(self, f"Expected Int, got {for_.var.type}", for_.var.lineno)
        self.visit(for_.body)

    def visit_Break(self, break_: Break):
        pass

    def visit_Continue(self, continue_: Continue):
        pass

    def visit_SymbolRef(self, ref: SymbolRef):
        pass

    def visit_MatrixRef(self, ref: MatrixRef):
        if ref.matrix.type == TS.undef():
            report_warn(self, "Matrix type could not be inferred", ref.lineno)
        elif not isinstance(ref.matrix.type, TS.Matrix):
            report_error(self, f"Expected Matrix, got {ref.matrix.type}", ref.lineno)

    def visit_VectorRef(self, ref: VectorRef):
        if ref.vector.type == TS.undef():
            report_warn(self, "Vector type could not be inferred", ref.lineno)
        elif not isinstance(ref.vector.type, TS.Vector):
            report_error(self, f"Expected Vector, got {ref.vector.type}", ref.lineno)

    def visit_Assign(self, assign: Assign):
        self.visit(assign.expr)
        assign.var.type = assign.expr.type

    def visit_Apply(self, apply: Apply):
        self.visit(apply.ref)
        self.visit_all(apply.args)
        assert isinstance(apply.ref, SymbolRef)
        ref_type = apply.ref.type

        if isinstance(ref_type, TS.Function):
            if ref_type.arity is not None and len(apply.args) != ref_type.arity:
                optional_s = "" if ref_type.arity == 1 else "s"
                report_error(self,
                             f"Function {apply.ref.name} expects {ref_type.arity} argument{optional_s}, got {len(apply.args)}",
                             apply.lineno)
            match ref_type.args:
                case None:
                    raise NotImplementedError
                case TS.VarArg(expected_type):
                    for arg in apply.args:
                        if arg.type != expected_type:
                            report_error(self,
                                         f"Function {apply.ref.name} expects {expected_type} arguments, got {arg.type}",
                                         apply.lineno)
                case TS.Type():
                    if apply.args[0].type != ref_type.args:
                        report_error(self,
                                     f"Function {apply.ref.name} expects {ref_type.args} argument, got {apply.args[0].type}",
                                     apply.lineno)
                case _:  # Tuple
                    for arg, expected_type in zip(apply.args, ref_type.args):
                        if arg.type != expected_type:
                            report_error(self,
                                         f"Function {apply.ref.name} expects {expected_type} arguments, got {arg.type}",
                                         apply.lineno)
        elif isinstance(ref_type, TS.undef):
            report_error(self, f"Undefined function {apply.ref.name} with {[arg.type for arg in apply.args]} arguments",
                         apply.lineno)
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

    def visit_Block(self, block: Block):
        self.visit_all(block.statements)
