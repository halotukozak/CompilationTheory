from dataclasses import dataclass
from typing import Any, Optional, TypeVar, Iterator

import TypeSystem as TS


# +- Tree -+- Statement -+
#          +- Block      |
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


class Tree:
    def __init__(self, lineno: Optional[int]):
        self.lineno = lineno or -1

    # for mypy
    def print_tree(self, indent_level: int) -> None:
        pass


class Statement(Tree):
    pass


# synthetic tree node to represent a block of statements
@dataclass(init=False)
class Block(Tree):
    statements: list[Statement]

    def __init__(self, statements: list[Statement], lineno: Optional[int] = None):
        super().__init__(lineno)
        self.statements = statements

    def __iter__(self) -> Iterator[Statement]:
        return iter(self.statements)


T = TypeVar('T', bound=TS.Type)


class Expr[T](Statement):
    def __init__(self, type_: Optional[TS.Type], lineno: Optional[int]):
        super().__init__(lineno)
        self.type = type_ or TS.undef()


@dataclass(init=False)
class Literal[T](Expr[T]):
    value: Any

    def __init__(self, value: Any, lineno: int, type_: TS.Type):
        super().__init__(type_, lineno)
        self.value = value

    @staticmethod
    def float(value: float, lineno: int) -> 'Literal[TS.Float]':
        return Literal(float(value), lineno, TS.Float())

    @staticmethod
    def string(value: str, lineno: int) -> 'Literal[TS.String]':
        return Literal(str(value), lineno, TS.String())

    @staticmethod
    def int(value: int, lineno: int) -> 'Literal[TS.Int]':
        return Literal(int(value), lineno, TS.Int())


@dataclass(init=False)
class Ref[T](Expr[T]):
    pass


@dataclass
class SymbolRef(Ref[T]):
    def __init__(self, name: str, lineno: Optional[int], type_: TS.Type):
        super().__init__(type_, lineno)
        self.name = name

    def copy(self) -> 'SymbolRef':
        return SymbolRef(self.name, self.lineno, self.type)


@dataclass(init=False)
class VectorRef(Ref[TS.Int | TS.Float]):
    vector: SymbolRef[TS.Vector]
    element: Expr[TS.Int]

    def __init__(self, vector: SymbolRef, element: Expr[TS.Int], lineno: int):
        super().__init__(TS.Int() | TS.Float(), lineno)
        self.vector = vector
        self.element = element


@dataclass(init=False)
class MatrixRef(Ref[TS.Int | TS.Float]):
    matrix: SymbolRef[TS.Matrix]

    def __init__(self, matrix: SymbolRef, row: Optional[Expr[TS.Int]], col: Optional[Expr[TS.Int]], lineno: int):
        super().__init__(TS.Int() | TS.Float(), lineno)
        self.matrix = matrix
        self.row = row
        self.col = col


@dataclass(init=False)
class Apply(Expr):
    ref: Ref
    args: list[Expr]

    def __init__(self, ref: Ref, args: list[Expr], lineno: int):
        super().__init__(TS.undef(), lineno)
        self.ref = ref
        self.args = args


@dataclass
class Range(Expr):
    start: Expr[TS.Int]
    end: Expr[TS.Int]
    lineno: int


@dataclass
class Assign[T](Statement):
    var: Ref[T]
    expr: Expr[T]
    lineno: int


@dataclass(init=False)
class If(Statement):
    condition: Expr[TS.Bool]
    then: Block
    else_: Optional[Block]

    def __init__(self, condition: Expr[TS.Bool], then: list[Statement], else_: Optional[list[Statement]], lineno: int):
        super().__init__(lineno)
        self.condition = condition
        self.then = Block(then)
        self.else_ = Block(else_) if else_ else None


@dataclass(init=False)
class While(Statement):
    condition: Expr
    body: Block

    def __init__(self, condition: Expr, body: list[Statement], lineno: int):
        super().__init__(lineno)
        self.condition = condition
        self.body = Block(body)
        self.lineno = lineno


@dataclass(init=False)
class For(Statement):
    var: SymbolRef
    range: Range
    body: Block

    def __init__(self, var: SymbolRef, range_: Range, body: list[Statement], lineno: int):
        super().__init__(lineno)
        self.var = var
        self.range = range_
        self.body = Block(body)


@dataclass
class Return[T](Statement):
    expr: Expr[T]
    lineno: int


@dataclass
class Continue(Statement):
    lineno: int


@dataclass
class Break(Statement):
    lineno: int
