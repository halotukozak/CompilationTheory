import typing
from dataclasses import dataclass
from typing import Tuple, Optional

from lab5.Result import Result


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

    def __str__(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:
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


# arity has no meaning in equality!
# todo: vector should be a metrix with 1 column/row
class Vector(Type):
    def __init__(self, arity: Optional[int] = None):
        self.arity = arity
        if arity is None:
            self.is_final = False

    def __str__(self):
        if self.arity is not None:
            return f"Vector[{self.arity}]"
        else:
            return f"Vector[?]"

    def __repr__(self):
        return self.__str__()


# arity has no meaning in equality!
class Matrix(Type):
    def __init__(self, rows: Optional[int] = None, cols: Optional[int] = None):
        self.rows = rows
        self.cols = cols
        if not self.rows or not self.cols:
            self.is_final = False

    def __str__(self):
        match self.arity:
            case (None, None):
                return "Matrix[?, ?]"
            case (None, b):
                return f"Matrix[?, {b}]"
            case (a, None):
                return f"Matrix[{a}, ?]"
            case (a, b):
                return f"Matrix[{a}, {b}]"

    def __repr__(self):
        return self.__str__()

    @property
    def arity(self):
        return self.rows, self.cols


@dataclass
class VarArg(Type):
    type: Type

    def __str__(self):
        return f"({self.type})*"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(repr(self))


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

    def __repr__(self):
        return self.__str__()

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


class FunctionTypeFactory(Function):
    is_final = False

    def __init__(self, args: None | Type | Tuple[Type, ...] | VarArg, result_hint: Type,
                 result_type_factory: typing.Callable[..., Result[Type]]):
        super().__init__(args, result_hint)
        self.result_type_factory = result_type_factory

    def __call__(self, args: list) -> Result[Type]:
        return self.result_type_factory(*args).map(lambda res: Function(self.args, res))

    def __str__(self):
        return f"TypeFunction: ({self.args}) -> {self.args}"  # todo: sth more informative

    def __repr__(self):
        return self.__str__()


class Int(Type):
    pass


class Float(Type):
    pass


class String(Type):
    pass


class Bool(Type):
    pass


def numerical() -> Type:
    return Int() | Float()
