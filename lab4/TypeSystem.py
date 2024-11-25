from dataclasses import dataclass
from typing import Tuple, Optional


class Type:
    is_final: bool = True

    def __eq__(self, other) -> bool:
        if isinstance(other, Any) or isinstance(self, Any):
            return True
        elif isinstance(other, AnyOf) and isinstance(self, AnyOf):
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
        if isinstance(other, Any) or isinstance(self, Any):
            return Any()
        elif isinstance(other, AnyOf) and isinstance(self, AnyOf):
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
        return hash(repr(self))


class undef(Type):
    is_final = False

class unit(Type):
    is_final = True


class Any(Type):
    is_final = True


class AnyOf(Type):
    all: list[Type]
    is_final = False

    def __init__(self, *types: Type):
        super().__init__()
        seen = set()
        self.all = [x for x in types if not (x in seen or seen.add(x))]

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
    def __init__(self, arity: Optional[int] = None):
        self.arity = arity
        if arity is None:
            self.is_final = False

    def __str__(self):
        if self.arity:
            return f"Vector[{self.arity}]"
        else:
            return f"Vector[?]"

    def __repr__(self):
        return self.__str__()


class Matrix(Type):
    def __init__(self, arity: Optional[Tuple[int, int]] = None):
        self.arity = arity
        if arity is None:
            self.is_final = False

    def __str__(self):
        if self.arity:
            return f"Matrix{list(self.arity)}"
        else:
            return f"Matrix[?]"

    def __repr__(self):
        return self.__str__()


@dataclass(repr=False)
class VarArg(Type):
    type: Type

    def __repr__(self):
        return f"({self.type})*"

    def __hash__(self):
        return hash(repr(self))


@dataclass(init=False, unsafe_hash=True)
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


class Bool(Type):
    pass


numerical = Int() | Float()
