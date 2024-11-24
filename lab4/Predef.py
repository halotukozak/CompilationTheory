from lab4 import TypeSystem as TS
from lab4.AST import SymbolRef
from lab4.TypeSystem import Or, AnyOf, VarArg

# todo: a lot of obscure (), maybe it can be omitted some way?
ts_float = TS.Float()
ts_int = TS.Int()
ts_bool = TS.Bool()
ts_matrix = TS.Matrix()
ts_vector = TS.Vector()

unary_numerical_type = Or(
    TS.Function(ts_int, ts_int),
    TS.Function(ts_float, ts_float),
)

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

binary_matrix_or_vector_type = Or(binary_matrix_type, binary_vector_type)

unary = {
    "-": unary_numerical_type,
    "'": TS.Function(ts_matrix, ts_matrix),
    "ones": TS.Function(ts_int, ts_vector),
    "eye": TS.Function(ts_int, ts_matrix),
    "zeros": TS.Function(ts_int, ts_vector),
}

binary = {
    "+": binary_numerical_type,
    "-": binary_numerical_type,
    "*": binary_numerical_type,
    "/": binary_numerical_type,
    "==": binary_numerical_condition_type,
    "!=": binary_numerical_condition_type,
    "<=": binary_numerical_condition_type,
    ">=": binary_numerical_condition_type,
    ">": binary_numerical_condition_type,
    "<": binary_numerical_condition_type,
    ".+": binary_matrix_or_vector_type,
    ".-": binary_matrix_or_vector_type,
    ".*": binary_matrix_or_vector_type,
    "./": binary_matrix_or_vector_type,
}

var_args = {
    "INIT": Or(
        TS.Function(VarArg(Or(ts_float, ts_int)), ts_vector),
        TS.Function(VarArg(ts_vector), ts_matrix),
    ),
    "PRINT": TS.Function(VarArg(TS.undef()), TS.undef()),
}

unary_keys = unary.keys()
binary_keys = binary.keys()


def get_type(name, args):
    match len(args):
        case 1 if name in unary_keys:
            return unary[name]
        case 2 if name in binary_keys:
            return binary[name]
        case _:
            return var_args[name]


def get(name, args):
    type_ = get_type(name, args)

    if isinstance(type_, TS.Function):
        return SymbolRef(name, None, type_.result)
    elif isinstance(type_, TS.AnyOf):
        res = []
        for t in type_.all:
            if isinstance(t, TS.Function):
                res.append(t.result)
            else:
                res.append(t)
        return SymbolRef(name, None, TS.AnyOf(*res))
    else:
        return SymbolRef(name, None, type_)