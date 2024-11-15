from dataclasses import dataclass


# +- Tree -+- Statement -+- Def ---------+
#                        |               +- FunDef
#                        |               +- VarDef
#                        |
#                        +- Expr --------+- Literal
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


@dataclass
class Vector(Expr):
    elements: list[Literal[int] | Literal[float]]
    lineno: int


@dataclass
class Matrix(Expr):
    vectors: list[Vector]
    lineno: int


class Ref[T](Expr[T]):
    pass


@dataclass
class SymbolRef[T](Ref[T]):
    name: str
    lineno: int


@dataclass
class VectorRef(Ref[Vector]):
    vector: SymbolRef[Vector]
    element: Literal[int]
    lineno: int


@dataclass
class MatrixRef(Ref[Matrix]):
    matrix: SymbolRef[Matrix]
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
    start: Literal[int]
    end: Literal[int]
    lineno: int


@dataclass
class Assign(Statement):  # [T]?
    var: Ref
    op: str
    expr: Expr
    lineno: int


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
