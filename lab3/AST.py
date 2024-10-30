from dataclasses import dataclass


# +- Tree -+- Statement -+
#                        +- Fun
#                        |
#                        +- Expr --------+- Ref --------+- VectorRef
#                        |               |              +- MatrixRef
#                        |               +- Apply
#                        |               +- Number
#                        |               +- Range
#                        |               +- Vector
#                        |               +- Matrix
#                        +- Assign
#                        +- If
#                        +- While
#                        +- For
#                        +- Return
#                        +- Continue
#                        +- Break
#                        +- Block


class Tree:
    pass


class Statement(Tree):
    def printTree(self):
        print(self)


@dataclass
class Fun(Statement):
    name: str


class Expr[T](Statement):
    pass


@dataclass
class Ref(Expr):  # [T]?
    symbol: str


@dataclass
class VectorRef(Expr):
    vector: Ref
    element: int


@dataclass
class MatrixRef(Expr):
    matrix: Ref
    row: int
    col: int


@dataclass
class Apply[T](Expr[T]):
    fun: Ref
    args: list[Expr]


@dataclass
class Number(Expr[int | float]):
    value: int | float


@dataclass
class Range(Expr[list[int]]):
    start: int
    end: int


@dataclass
class Vector(Expr[list[Number]]):
    elements: list[Number]


@dataclass
class Matrix(Expr[list[Vector]]):
    vectors: list[Vector]


@dataclass
class Assign(Statement):  # [T]?
    var: Ref
    op: str
    expr: Expr


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


@dataclass
class Block(Statement):
    statements: list[Statement]

    def __init__(self, *statements):
        self.statements = list(statements)
