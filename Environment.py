from typing import Optional, Callable


class Vector:
    def __init__(self, source: list[int]):
        self.source = source

    def __setitem__(self, index: int, value: int):
        self.source[index] = value

    def __getitem__(self, index: int) -> int:
        return self.source[index]


class Matrix:
    def __init__(self, source: list[Vector]):
        self.source = source

    def __setitem__(self, row: int, value: Vector):
        self.source[row] = value

    def __getitem__(self, row: int) -> Vector:
        return self.source[row]


class Env(object):
    memory = {}
    functions: dict[str, Callable] = {}

    def __init__(self, parent: 'Env'):
        self.parent = parent

    def create[T](self, name: str, value: Optional[T] = None):
        self.memory[name] = value

    def update(self, name: str, value) -> bool:
        if name in self.memory.keys():
            self.memory[name] = value
            return True
        return self.parent and self.parent.update(name, value)

    def get_value(self, name: str):
        if name in self.memory.keys():
            return self.memory[name]
        return self.parent.get_value(name)

    def get_function(self, name: str):
        if name in self.functions.keys():
            return self.functions[name]
        if self.parent:
            return self.parent.get_function(name)


def init_lambda(*args):
    if isinstance(args[0], int):
        return Vector(list(args))
    else:
        return Matrix(list(args))


class EnvTable(object):
    global_env = Env(None)
    global_env.functions = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
        'PRINT': lambda *args: print(*args),
        'zeros': lambda n: Matrix([[0] * n] * n),
        'ones': lambda n: Matrix([[1] * n] * n),
        'eye': lambda n: Matrix([Vector([1 if i == j else 0 for j in range(n)]) for i in range(n)]),
        'INIT': init_lambda,
        '==': lambda a, b: a == b,
        '!=': lambda a, b: a != b,
        '<=': lambda a, b: a <= b,
        '>=': lambda a, b: a >= b,
        '<': lambda a, b: a < b,
        '>': lambda a, b: a > b,

    }

    actual_env = global_env

    def push_env(self, new_env: Env):
        self.actual_env = new_env

    def pop_env(self):
        self.actual_env = self.actual_env.parent
