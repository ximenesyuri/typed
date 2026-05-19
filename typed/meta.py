from typed.core import lazy

__imports__ = {
    "typed.mods.meta.base": [
        "EMPTY",
        "NILL", "INT", "BOOL", "STR", "FLOAT", "BYTES",
        "TUPLE", "LIST", "SET", "DICT"
        ]

}

if lazy(__imports__):
    from typed.mods.meta.base import (
        EMPTY,    
        NILL, ANY, INT, BOOL, STR, FLOAT, BYTES,
        TUPLE, LIST, SET, DICT
    )

#     from typed.mods.meta.func import (
#         CALLABLE, BUILTIN, FUNCTION, LAMBDA, PARTIAL,
#         CLASS, BOUND_METHOD, UNBOUND_METHOD, METHOD,
#         ATTR_FUNC, DOM_FUNC, COD_FUNC, COMP_FUNC,
#         DOM_HINTED, COD_HINTED, HINTED,
#         DOM_TYPED, COD_TYPED, TYPED,
#         FACTORY, OPERATION, DEPENDENT, CONDITION,
#         LAZY
#     )
