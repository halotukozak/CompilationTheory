from lab4 import TypeSystem as TS
from lab4.AST import SymbolRef
from lab4.TypeSystem import AnyOf, VarArg, Type


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
ts_string = TS.String()

unary_numerical_type = TS.Function(ts_int, ts_int) | TS.Function(ts_float, ts_float)

binary_numerical_type = AnyOf(
    TS.Function((ts_int, ts_int), ts_int),
    TS.Function((ts_float, ts_float), ts_float),
    TS.Function((ts_int, ts_float), ts_float),
    TS.Function((ts_float, ts_int), ts_float),
)

binary_numerical_condition_type = AnyOf(
    TS.Function((ts_int, ts_int), ts_bool),
    TS.Function((ts_float, ts_float), ts_bool),
    TS.Function((ts_int, ts_float), ts_bool),
    TS.Function((ts_float, ts_int), ts_bool),
)

binary_matrix_type = TS.Function((ts_matrix, ts_matrix), ts_matrix)
binary_vector_type = TS.Function((ts_vector, ts_vector), ts_vector)

unary = prepare({
    "UMINUS": unary_numerical_type,  # need to be distinct from binary
    "'": TS.Function(ts_matrix, ts_matrix),
    "eye": TS.Function(ts_int, ts_matrix),
    "zeros": TS.Function(ts_int, ts_matrix),
    "ones": TS.Function(ts_int, ts_matrix),
})

binary = prepare({
    "+": binary_numerical_type | binary_matrix_type | binary_vector_type,
    "-": binary_numerical_type | binary_matrix_type | binary_vector_type,
    "*": binary_numerical_type | binary_matrix_type | binary_vector_type,
    "/": binary_numerical_type | binary_matrix_type | binary_vector_type,
    "==": binary_numerical_condition_type,
    "!=": binary_numerical_condition_type,
    "<=": binary_numerical_condition_type,
    ">=": binary_numerical_condition_type,
    ">": binary_numerical_condition_type,
    "<": binary_numerical_condition_type,
    ".+": (binary_matrix_type | binary_vector_type),
    ".-": (binary_matrix_type | binary_vector_type),
    ".*": (binary_matrix_type | binary_vector_type),
    "./": (binary_matrix_type | binary_vector_type),
})

var_args = prepare({
    "INIT": TS.Function(VarArg(ts_float | ts_int), ts_vector) |
            TS.Function(VarArg(ts_vector), ts_matrix),
    "PRINT": TS.Function(VarArg(ts_string | ts_float | ts_int), ts_string),
})

symbols = {**unary, **binary, **var_args}


def get_symbol(name: str) -> SymbolRef:
    return symbols[name].copy()
