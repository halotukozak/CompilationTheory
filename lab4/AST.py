from dataclasses import dataclass
from typing import TypeVar

from lab4.TypeSystem import Type

# +- Tree -+- Statement -+- Def ---------+
#                        |               +- FunDef
#                        |               +- VarDef
#                        |
#                        +- Expr --------+- Literal
#                        |               +- Apply
#                        |               +- Number
#                        |               +- String
#                        |               +- Range
#                        |               +- Ref --------+- VectorRef
#                        |                              +- MatrixRef
#                        |                              +- SymbolRef
#                        +- Assign
#                        +- If
#                        +- While
#                        +- For
#                        +- Return
#                        +- Continue
#                        +- Break

T = TypeVar('T', bound='Type')


class Tree:
    lineno: int

    def __init__(self, lineno: int):
        self.lineno = lineno


class Statement(Tree):
    pass


class Def(Statement):
    pass


class FunDef(Def):
    pass


class VarDef(Def):
    pass


class Expr[T](Statement):
    pass


@dataclass
class Literal[T](Expr[T]):
    value: T
    lineno: int

    @staticmethod
    def int(value, lineno: int):
        return Literal(int(value), lineno)

    @staticmethod
    def float(value: float, lineno: int):
        return Literal(float(value), lineno)

    @staticmethod
    def string(value, lineno: int):
        return Literal(str(value), lineno)


class Ref[T](Expr[T]):
    pass


@dataclass
class SymbolRef[T](Ref[T]):
    name: str
    lineno: int


@dataclass
class VectorRef(Ref[Type.Vector]):
    vector: SymbolRef[Type.Vector]
    element: Literal[int]
    lineno: int


@dataclass
class MatrixRef(Ref[Type.Matrix]):
    matrix: SymbolRef[Type.Matrix]
    row: Literal[int]
    col: Literal[int]
    lineno: int


@dataclass
class Apply[T](Expr[T]):
    fun: Ref[T]
    args: list[Expr]
    lineno: int


@dataclass
class Range(Expr):
    start: Expr[int]
    end: Expr[int]
    lineno: int


class Assign(Statement):  # [T]?
    var: Ref
    expr: Expr
    lineno: int

    def __init__(self, var: Ref, op: str, expr: Expr, lineno: int):
        super().__init__(lineno)
        self.var = var
        match op:
            case "=":
                self.expr = expr
            case _:
                self.expr = Apply(SymbolRef(op[:-1], lineno), [var, expr], lineno)


@dataclass
class If(Statement):
    condition: Expr[bool]
    then: list[Statement]
    else_: list[Statement] | None
    lineno: int


@dataclass
class While(Statement):
    condition: Expr[bool]
    body: list[Statement]
    lineno: int


@dataclass
class For(Statement):
    var: SymbolRef
    range: Range
    body: list[Statement]
    lineno: int


@dataclass
class Return(Statement):
    expr: Expr
    lineno: int


@dataclass
class Continue(Statement):
    lineno: int


@dataclass
class Break(Statement):
    lineno: int
