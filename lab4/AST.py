from dataclasses import dataclass
from typing import TypeVar, Any, Optional

from lab4 import TypeSystem as TS

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


class Statement(Tree):
    pass


class Def(Statement):
    pass


class FunDef(Def):
    pass


class VarDef(Def):
    pass


class Expr[T](Statement):
    type: T


@dataclass
class Literal[T](Expr[T]):
    value: Any
    lineno: int
    type: T

    @staticmethod
    def int(value, lineno: int):
        return Literal(int(value), lineno, TS.Int())

    @staticmethod
    def float(value: float, lineno: int):
        return Literal(float(value), lineno, TS.Float())

    @staticmethod
    def string(value, lineno: int):
        return Literal(str(value), lineno, TS.String())


@dataclass(init=False)
class Ref[T](Expr[T]):
    pass


@dataclass
class SymbolRef[T](Ref[T]):
    name: str
    lineno: Optional[int]
    type: T


@dataclass
class VectorRef(Ref[TS.Vector]):
    vector: SymbolRef[TS.Vector]
    element: Literal[TS.Int]
    lineno: int


@dataclass
class MatrixRef(Ref[TS.Matrix]):
    matrix: SymbolRef[TS.Matrix]
    row: Literal[TS.Int]
    col: Literal[TS.Int]
    lineno: int


@dataclass(init=False)
class Apply[T](Expr[T]):
    fun: Ref[T]
    args: list[Expr]
    lineno: int

    def __init__(self, fun: Ref[T], args: list[Expr], lineno: int):
        self.fun = fun
        self.args = args
        self.type = fun.type  # todo: result
        self.lineno = lineno


@dataclass
class Range(Expr):
    start: Expr[TS.Int]
    end: Expr[TS.Int]
    lineno: int


@dataclass
class Assign(Statement):
    var: Ref
    expr: Expr
    lineno: int


@dataclass
class If(Statement):
    condition: Expr[TS.Bool]
    then: list[Statement]
    else_: list[Statement] | None
    lineno: int


@dataclass
class While(Statement):
    condition: Expr[TS.Bool]
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
