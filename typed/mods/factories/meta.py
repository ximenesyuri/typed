from functools import lru_cache as cache
from typed.mods.types.base import TYPE, Nill
from typed.mods.meta.base import _TYPE_
from typed.mods.helper.helper import _name, _name_list

@cache
def PARAMETRIC(*types, factory):
    from typed.mods.types.base import TYPE
    from typed.mods.types.func import Factory

    if not factory:
        raise ValueError(
            "Missing value in 'PARAMETRIC' factory\n"
            f" ==> 'factory': required argument were not set."
        )

    if not types:
        return factory

    if not isinstance(factory, Factory):
        raise TypeError(
            "Wrong type in PARAMETRIC factory: \n"
            f" ==> {_name(factory)}: has unexpected type\n"
            f"     [expected_type] a subtype of Factory\n"
            f"     [received_type] {_name(type(factory))}"
        )

    for typ in types:
        if not isinstance(typ, TYPE):
            raise TypeError(
                "Wrong type in PARAMETRIC factory: \n"
                f" ==> {_name(typ)}: has unexpected type\n"
                f"     [expected_type] a subtype of TYPE\n"
                f"     [received_type] {_name(type(typ))}"
            )

    TYPES = (TYPE(typ) for typ in types)
    class _PARAMETRIC_(*TYPES):
        def __instancecheck__(cls, instance):
            return all(isinstance(instance, typ) for typ in types)
        def __subclasscheck__(cls, subclass):
            return all(issubclass(subclass, typ) for typ in types)
        def __call__(self, *args, **kwargs):
            if not args and not kwargs:
                return self._type()
            elif args and isinstance(args[0], type):
                return self._factory(*args, **kwargs)
            else:
                return self._type(*args, **kwargs)

    class_name = _name(base_type)
    return _PARAMETRIC_(class_name, (base_type,), {
        "__display__": class_name,
        "base_type": base_type,
        "factory": factory
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
