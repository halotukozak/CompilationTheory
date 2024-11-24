import builtins
from typing import Tuple, Optional

from attr import dataclass


class Type:
    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return type(self).__name__

    def __or__(self, other):
        return Or(self, other)


class undef(Type):
    pass


class AnyOf(Type):
    all: tuple[Type, ...]

    def __init__(self, *types: Type):
        self.all = types

    def __repr__(self):
        return ' | '.join(map(str, self.all))

    def __str__(self):
        return ' | '.join(map(str, self.all))


class Or(AnyOf):
    def __init__(self, left: Type, right: Type):
        super().__init__(left, right)


class Vector(Type):
    arity: Optional[int] = None


@dataclass(repr=False)
class VarArg(Type):
    type: Type

    def __repr__(self):
        return f"({self.type})*"


@dataclass(init=False)
class Function(Type):
    args: None | Type | Tuple[Type, ...] | VarArg
    arity: int
    result: Type

    def __init__(self, args: None | Type | Tuple[Type, ...] | VarArg, result: Type):
        if args is None:
            self.args = None
            self.arity = 0
        elif isinstance(args, Type):
            self.args = args
            self.arity = 1
        elif isinstance(args, Tuple):
            self.args = args
            self.arity = len(args)
        elif isinstance(args, VarArg):
            self.args = args.type
            self.arity = -1

        self.result = result

    def __str__(self):
        if isinstance(self.args, builtins.type):
            return f"({self.args.original}) -> {self.result}"
        else:
            return f"({self.args}) -> {self.result}"


class Int(Type):
    pass


class Float(Type):
    pass


class String(Type):
    pass


class Matrix(Type):
    pass


class Bool(Type):
    pass
