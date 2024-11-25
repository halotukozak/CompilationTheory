from typing import Callable, Any

from lab4 import TypeSystem as TS
from lab4.AST import SymbolRef
from lab4.TypeSystem import VarArg, Type


# these dictionaries should be more generic, but there is so much boilerplate in the code

def parse_result(type_: Type) -> Type:
    if isinstance(type_, TS.Function):
        return type_.result
    elif isinstance(type_, TS.AnyOf):
        res = set()
        for t in type_.all:
            if isinstance(t, TS.Function):
                res.add(t.result)
            else:
                res.add(t)
        return TS.AnyOf(*res)
    else:
        return type_


def prepare(dict_: dict[str, Type]) -> dict[str, SymbolRef]:
    return {name: SymbolRef(name, None, type_) for name, type_ in dict_.items()}


# todo: a lot of obscure (), maybe it can be omitted some way?
ts_undef = TS.undef()
ts_float = TS.Float()
ts_int = TS.Int()
ts_bool = TS.Bool()
ts_matrix = TS.Matrix()
ts_vector = TS.Vector()

unary_numerical_type = TS.Function(ts_int, ts_int) | TS.Function(ts_float, ts_float)
unary_vector_type = TS.Function(ts_vector, ts_vector)
unary_matrix_type = TS.Function(ts_matrix, ts_matrix)

binary_numerical_type = TS.Function((ts_int, ts_int), ts_int) \
                        | TS.Function((TS.numerical, TS.numerical), ts_float)

binary_numerical_condition_type = TS.Function((TS.numerical, TS.numerical), ts_bool)

binary_matrix_type = TS.Function((ts_matrix, ts_matrix), ts_matrix)
binary_vector_type = TS.Function((ts_vector, ts_vector), ts_vector)

unary = prepare({
    "UMINUS": unary_numerical_type | unary_vector_type | unary_matrix_type,
    "'": TS.Function(ts_matrix, ts_matrix) | TS.Function(ts_vector, ts_vector),
    "eye": TS.Function(ts_int, ts_matrix),
    "zeros": TS.Function(ts_int, ts_matrix),
    "ones": TS.Function(ts_int, ts_matrix),
})

scalar_type = TS.Function((ts_matrix, TS.numerical), ts_matrix) \
              | TS.Function((ts_vector, TS.numerical), ts_vector)

binary = prepare({
    "+": binary_numerical_type | binary_matrix_type | binary_vector_type,
    "-": binary_numerical_type | binary_matrix_type | binary_vector_type,
    "*": binary_numerical_type | binary_matrix_type | binary_vector_type | scalar_type,
    "/": binary_numerical_type | binary_matrix_type | binary_vector_type | scalar_type,
    "==": binary_numerical_condition_type,
    "!=": binary_numerical_condition_type,
    "<=": binary_numerical_condition_type,
    ">=": binary_numerical_condition_type,
    ">": binary_numerical_condition_type,
    "<": binary_numerical_condition_type,
    ".+": scalar_type,
    ".-": scalar_type,
    ".*": scalar_type,
    "./": scalar_type,
})

var_args = prepare({
    "INIT": TS.Function(VarArg(TS.numerical), ts_vector) |
            TS.Function(VarArg(ts_vector), ts_matrix),
    "PRINT": TS.Function(VarArg(TS.Any()), ts_undef),
})

init_callables = {
    "INIT_VECTOR": lambda n: SymbolRef(
        "INIT_VECTOR",
        None,
        TS.Function(VarArg(TS.numerical), TS.Vector(n))
    ),
    "INIT_MATRIX": lambda n, m: SymbolRef(
        "INIT_MATRIX",
        None,
        TS.Function(VarArg(TS.Vector(m)), TS.Matrix((n, m)))
    ),
}

vector_callables = {
    "-_Vector": lambda n, sym: SymbolRef(
        f"{sym}_Vector",
        None,
        TS.Function(TS.Vector(n), TS.Vector(n))
    ),
    "'_Vector": lambda n, sym: SymbolRef(
        f"{sym}_Vector",
        None,
        TS.Function(TS.Vector(n), TS.Vector(n))
    ),
    "BINARY_Vector": lambda n, sym: SymbolRef(
        f"{sym}_Vector",
        None,
        TS.Function((TS.Vector(n), TS.Vector(n)), TS.Vector(n))
    ),
    "SCALAR_Vector": lambda n, sym: SymbolRef(
        f"{sym}_Vector",
        None,
        TS.Function((TS.Vector(n), TS.numerical), TS.Vector(n))
    ),
}

matrix_callables = {
    "-_Matrix": lambda n, m, sym: SymbolRef(
        f"{sym}_Metrix",
        None,
        TS.Function(TS.Matrix((n, m)), TS.Matrix((n, m)))
    ),
    "'_Matrix": lambda n, m, sym: SymbolRef(
        "'_Metrix",
        None,
        TS.Function(TS.Matrix((n, m)), TS.Matrix((m, n)))
    ),
    "BINARY_Matrix": lambda n, m, sym: SymbolRef(
        f"{sym}_Matrix",
        None,
        TS.Function((TS.Matrix((n, m)), TS.Matrix((n, m))), TS.Matrix((n, m)))
    ),
    "SCALAR_Matrix": lambda n, m, sym: SymbolRef(
        f"{sym}_Matrix",
        None,
        TS.Function((TS.Matrix((n, m)), TS.numerical), TS.Matrix((n, m)))
    ),
    "*_Matrix": lambda n, m, p, sym: SymbolRef(
        f"*_Matrix",
        None,
        TS.Function((TS.Matrix((n, m)), TS.Matrix((m, p))), TS.Matrix((n, p)))
    ),
    "ones_Matrix": lambda n: SymbolRef(
        "ones_Matrix",
        None,
        TS.Function(ts_int, TS.Matrix((n, n)))
    ),
    "zeros_Matrix": lambda n: SymbolRef(
        "zeros_Matrix",
        None,
        TS.Function(ts_int, TS.Matrix((n, n)))
    ),
    "eye_Matrix": lambda n: SymbolRef(
        "eye_Matrix",
        None,
        TS.Function(ts_int, TS.Matrix((n, n)))
    ),
}

callables = {**init_callables, **vector_callables, **matrix_callables}

symbols = {**unary, **binary, **var_args, **callables}


# todo: maybe split into two functions?
def get_symbol(name: str) -> SymbolRef | Callable[[Any], SymbolRef]:
    res = symbols[name]
    if isinstance(res, SymbolRef):
        return res.copy()
    else:
        return res
