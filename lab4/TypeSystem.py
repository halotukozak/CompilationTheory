import builtins
from typing import Tuple, Optional

from attr import dataclass


class Type:
    def __eq__(self, other) -> bool:
        if isinstance(other, AnyOf) and isinstance(self, AnyOf):
            return set(self.all).intersection(other.all) != set()
        elif isinstance(self, AnyOf):
            return other in self
        elif isinstance(other, AnyOf):
            return self in other
        else:
            return type(self) == type(other)

    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return type(self).__name__

    def __or__(self, other):
        if isinstance(other, AnyOf) and isinstance(self, AnyOf):
            return AnyOf(*self.all, *other.all)
        elif isinstance(self, AnyOf):
            return AnyOf(*self.all, other)
        elif isinstance(other, AnyOf):
            return AnyOf(self, *other.all)
        elif self == other:
            return self
        else:
            return Or(self, other)

    def __hash__(self):
        return hash(str(self))


class undef(Type):
    pass


class AnyOf(Type):
    all: set[Type]

    def __init__(self, *types: Type):
        self.all = set(types)

    def __repr__(self):
        return ' | '.join(map(str, self.all))

    def __str__(self):
        return ' | '.join(map(str, self.all))

    def __iter__(self):
        return iter(self.all)


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
    arity: Optional[int]
    result: Type

    def __init__(self, args: None | Type | Tuple[Type, ...] | VarArg, result: Type):
        if args is None:
            self.arity = 0
        elif isinstance(args, VarArg):
            self.arity = None
        elif isinstance(args, Type):
            self.arity = 1
        elif isinstance(args, Tuple):
            self.arity = len(args)
        self.args = args
        self.result = result

    def __str__(self):
        if isinstance(self.args, builtins.type):
            return f"({self.args.original}) -> {self.result}"
        else:
            return f"({self.args}) -> {self.result}"

    def takes(self, args: list[Type]) -> bool:
        if self.args is None:
            return not args
        elif isinstance(self.args, VarArg):
            return all(a == self.args.type for a in args)
        elif isinstance(self.args, Type):
            return len(args) == 1 and self.args == args[0]
        elif isinstance(self.args, Tuple):
            return len(self.args) == len(args) and all(a == b for a, b in zip(self.args, args))
        else:
            return False


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
