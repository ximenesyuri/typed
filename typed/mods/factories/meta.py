from typing import Tuple as Tuple_, Type
from functools import lru_cache as cache
from typed.mods.types.base import TYPE, Nill
from typed.mods.meta.base import _TYPE_
from typed.mods.helper.helper import _name, _name_list

@cache
def SUBTYPES(*types: Tuple_[Type]) -> Type:
    """
    Build the metatype of subtypes of a given types.
        > An object of `SUBTYPE(X, Y, ...)`
        > is a type T such that issubclass(T, K) is True
        > for some K in (X, Y, ...)
    """
    for typ in types:
        if not issubclass(type(typ), TYPE):
            raise TypeError(
                "Wrong type in SUBTYPES metafactory: \n"
                f" ==> {_name(typ)}: has unexpected type\n"
                f"     [expected_type] a subtype of TYPE"
                f"     [received_type] {_name(type(typ))}"
            )

    class _SUBTYPES_(_TYPE_):
        def __instancecheck__(cls, instance):
            return any(issubclass(instance, typ) for typ in types)

    class_name = f"SUBTYPES({_name_list(*types)})"
    return _SUBTYPES_(class_name, (), {
        "__display__": class_name,
        "__null__": Nill
    })
SUB = SUBTYPES

@cache
def NOT(*types: Tuple_[Type]) -> Type:
    """
    Build the metatype of types which are not
    the given types.
        > An object of `NOT(X, Y, ..)`
        > is any type T such that
        > T is not X, Y, ...
    """
    for typ in types:
        if not issubclass(type(typ), TYPE):
            raise TypeError(
                "Wrong type in NOT metafactory: \n"
                f" ==> {_name(typ)}: has unexpected type\n"
                f"     [expected_type] a subtype of TYPE"
                f"     [received_type] {_name(type(typ))}"
            )

    class _NOT_(_TYPE_):
        def __instancecheck__(cls, instance):
            return not any(instance is t for t in types)

    class_name = f"NOT({_name_list(*types)})"
    return _NOT_(class_name, (), {
        "__display__": class_name,
        "__null__": Nill
    })
