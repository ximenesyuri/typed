from functools import lru_cache as cache
from typed.mods.types.base import TYPE, Nill, Str, List
from typed.mods.meta.base import _TYPE_
from typed.mods.helper.general import _name, _name_list

@cache
def ATTR(attributes):
    if isinstance(attributes, Str):
        attributes = (attributes,)
    elif not isinstance(attributes, List):
        raise TypeError("attributes must be a string or a list of strings")

    class _ATTR_(_TYPE_):
        def __init__(cls, name, bases, dct, attributes=None):
            super().__init__(name, bases, dct)
            if attributes:
                setattr(cls, '__attrs__', attributes)

        def __instancecheck__(cls, instance):
            attrs = getattr(cls, '__attrs__', None)
            if attrs:
                return all(hasattr(instance, attr) for attr in attrs)
            return False

    class_name = f'ATTR({_name_list(*attributes)})'

    from typed.mods.types.base import Nill
    return _ATTR_(class_name, (TYPE,), {
        '__attrs__': tuple(attributes),
        "__null__": Nill,
        "__display__": class_name
    })

@cache
def SUBTYPES(*types):
    """
    Build the metatype of subtypes of a given types.
        > An object of `SUBTYPE(X, Y, ...)`
        > is a type T such that issubclass(T, K) is True
        > for some K in (X, Y, ...)
    """
    if not types:
        from typed.mods.types.base import Nill
        return Nill
    for typ in types:
        if not isinstance(typ, TYPE):
            raise TypeError(
                "Wrong type in SUBTYPES metafactory: \n"
                f" ==> {_name(typ)}: has unexpected type\n"
                f"     [expected_type] a subtype of TYPE\n"
                f"     [received_type] {_name(type(typ))}"
            )

    class _SUBTYPES_(_TYPE_):
        def __instancecheck__(cls, instance):
            return any(issubclass(instance, typ) for typ in types)

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, cls)

    class_name = f"SUBTYPES({_name_list(*types)})"
    return _SUBTYPES_(class_name, (), {
        "__display__": class_name,
        "__null__": Nill
    })
SUB = SUBTYPES

@cache
def NOT(*types):
    """
    Build the metatype of types which are not
    the given types.
        > An object of `NOT(X, Y, ..)`
        > is any type T such that
        > T is not X, Y, ...
    """
    for typ in types:
        if not isinstance(typ, TYPE):
            raise TypeError(
                "Wrong type in NOT metafactory: \n"
                f" ==> {_name(typ)}: has unexpected type\n"
                f"     [expected_type] a subtype of TYPE\n"
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
