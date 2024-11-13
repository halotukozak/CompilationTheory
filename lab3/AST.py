from dataclasses import dataclass

# +- Tree -+- Statement -+
#                        +- Expr --------+
#                        |               +- Apply
#                        |               +- Number
#                        |               +- String
#                        |               +- Range
#                        |               +- Vector
#                        |               +- Matrix
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

class Tree:
    pass


class Statement(Tree):
    pass

class Expr[T](Statement):
    pass


@dataclass
class Vector(Expr):
    elements: list[int | float]


@dataclass
class Matrix(Expr):
    vectors: list[Vector]


class Ref[T](Expr[T]):
    pass


@dataclass
class SymbolRef[T](Ref[T]):
    symbol: str


@dataclass
class VectorRef(Ref[Vector]):
    vector: Ref[Vector]
    element: int


@dataclass
class MatrixRef(Ref[Matrix]):
    matrix: SymbolRef
    row: int
    col: int


@dataclass
class Apply[T](Expr[T]):
    fun: Ref
    args: list[Expr | int | float | str]


@dataclass
class Range(Expr):
    start: Expr[int] | int
    end: Expr[int] | int


@dataclass
class Assign(Statement):  # [T]?
    var: Ref
    op: str
    expr: Expr | int | float | str


@dataclass
class If(Statement):
    condition: Expr[bool]
    then: list[Statement]
    else_: list[Statement] | None


@dataclass
class While(Statement):
    condition: Expr[bool]
    body: list[Statement]


@dataclass
class For(Statement):
    var: Ref
    range: Range
    body: list[Statement]


@dataclass
class Return(Statement):
    expr: Expr


class Continue(Statement):
    pass


class Break(Statement):
    pass
