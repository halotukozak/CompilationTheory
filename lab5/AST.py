from dataclasses import dataclass
from typing import Any, Optional

from lab5 import TypeSystem as TS


# +- Tree -+- Statement -+- Def ---------+
#          +- Block      |               +- FunDef
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


class Tree:
    lineno: int


class Statement(Tree):
    pass


# synthetic tree node to represent a block of statements
@dataclass
class Block(Tree):
    statements: list[Statement]

    def __iter__(self):
        return iter(self.statements)


class Def(Statement):
    pass


class FunDef(Def):
    pass


class VarDef(Def):
    pass


class Expr(Statement):
    type: TS.Type = TS.undef()


@dataclass
class Literal(Expr):
    value: Any
    lineno: int
    type: TS.Type

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
class Ref(Expr):
    pass


@dataclass
class SymbolRef(Ref):
    name: str
    lineno: Optional[int]
    type: TS.Type = TS.undef()

    def copy(self):
        return SymbolRef(self.name, self.lineno, self.type)


@dataclass
class VectorRef(Ref):
    vector: SymbolRef
    element: Literal
    lineno: int
    type = TS.Int() | TS.Float()


@dataclass
class MatrixRef(Ref):
    matrix: SymbolRef
    row: Literal
    col: Literal
    lineno: int
    type = TS.Int() | TS.Float()


@dataclass(init=False)
class Apply(Expr):
    ref: Ref
    args: list[Expr]
    lineno: int

    def __init__(self, ref: Ref, args: list[Expr], lineno: int):
        self.ref = ref
        self.args = args
        self.lineno = lineno


@dataclass
class Range(Expr):
    start: Expr
    end: Expr
    lineno: int


@dataclass
class Assign(Statement):
    var: Ref
    expr: Expr
    lineno: int


@dataclass(init=False)
class If(Statement):
    condition: Expr
    then: Block
    else_: Optional[Block]
    lineno: int

    def __init__(self, condition: Expr, then: list[Statement], else_: Optional[list[Statement]], lineno: int):
        self.condition = condition
        self.then = Block(then)
        self.else_ = Block(else_) if else_ else None
        self.lineno = lineno


@dataclass(init=False)
class While(Statement):
    condition: Expr
    body: Block
    lineno: int

    def __init__(self, condition: Expr, body: list[Statement], lineno: int):
        self.condition = condition
        self.body = Block(body)
        self.lineno = lineno


@dataclass(init=False)
class For(Statement):
    var: SymbolRef
    range: Range
    body: Block
    lineno: int

    def __init__(self, var: SymbolRef, range_: Range, body: list[Statement], lineno: int):
        self.var = var
        self.range = range_
        self.body = Block(body)
        self.lineno = lineno


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
