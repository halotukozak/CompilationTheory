import numbers
from dataclasses import dataclass


class Block:
    pass


class Expr:
    pass


@dataclass
class Operator:
    sign: str


@dataclass
class UnaryOperator(Expr):
    op: Operator
    expr: Expr


@dataclass
class BinaryOperator(Expr):
    left: Expr
    right: Expr


@dataclass
class AssignmentOperator(Operator):
    pass

@dataclass
class ConditionOperator(Operator):
    pass
@dataclass
class Number(Expr):
    value: numbers.Number


@dataclass
class String(Expr):
    value: str


@dataclass
class Condition(Expr):
    left: Expr
    op: ConditionOperator
    right: Expr

@dataclass
class If(Expr):
    condition: Condition
    then: Expr
    else_: Expr


@dataclass
class While(Expr):
    condition: Condition
    body: Expr


@dataclass
class Range(Expr):
    start: Number
    end: Number


@dataclass
class Var(Expr):
    name: str
    value: Expr


class Statement(Block):
    pass


@dataclass
class For(Expr):
    var: Var
    range: Range
    block: Block


@dataclass
class Assignment(Block):
    var: Var
    op: AssignmentOperator
    expr: Expr


class CONTINUE(Block):
    pass


class Break(Block):
    pass


@dataclass
class Return(Block):
    expr: Expr


@dataclass
class VarArg(Expr):
    elements: list[Expr]
