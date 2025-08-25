import re
from functools import lru_cache as cache
from typing import Tuple as Tuple_, Type, Any as Any_
from types import FunctionType
from typed.mods.helper.null import _null, _null_from_list
from typed.mods.helper.helper import (
    _hinted_domain,
    _hinted_codomain,
    _name,
    _name_list,
)

@cache
def Inter(*types: Tuple_[Type]) -> Type:
    """
    Build the 'intersection' of types:
        > an object 'p' of the Inter(X, Y, ...)
        > is an object of every 'X, Y, ...'
    """
    for t in types:
        if not isinstance(t, type):
            raise TypeError(
                "Wrong type in Union factory: \n"
                f" ==> {_name(t)}: has unexpected type\n"
                 "     [expected_type] TYPE\n"
                f"     [received_type] {_name(type(t))}"
            )
    if types:
        def _key(t):
            return (t.__module__, getattr(t, '__qualname__', t.__name__))
        unique = set(types)
        sorted_types = tuple(sorted(unique, key=_key))
        if len(sorted_types) == 1:
            return sorted_types[0]
        if sorted_types != types:
            return Inter(*sorted_types)
        unique_types = sorted_types
    else:
        unique_types = ()

    non_builtin_types = [t for t in unique_types if not t.__module__ == 'builtins']

    types_ = (type(typ) for typ in unique_types)
    class _Inter(*types_):
        def __instancecheck__(cls, instance):
            return all(isinstance(instance, t) for t in non_builtin_types)
        def __subclasscheck__(cls, subclass):
            return all(issubclass(subclass, t) for t in unique_types)

    __null__ = list(set(_null(t) for t in types))

    class_name = f"Inter({_name_list(*unique_types)})"
    try:
        return _Inter(class_name, unique_types, {
            '__display__': class_name,
            '__types__': unique_types,
            '__null__': __null__[0] if len(__null__) == 1 else None
        })
    except Exception as e:
        return _Inter(class_name, (), {
            '__display__': class_name,
            '__types__': unique_types,
            '__null__': __null__[0] if len(__null__) == 1 else None
        })

@cache
def Filter(X: Type, f: Tuple_[FunctionType]) -> Type:
    real_filters = []
    from typed.mods.types.base import Any
    from typed.mods.types.base import Condition
    if not isinstance(f, Condition):
        raise TypeError(
            "Wrong type in Filter factory: \n"
            f" ==> {_name(f)}: has unexpected type\n"
             "     [expected_type] Condition\n"
            f"     [received_type] {_name(type(f))}"
        ) 
    class _Filter(type(X)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, X):
                return False
            return f(instance)

    class_name = f"Filter({_name(X)}; {_name(f)})"
    Filter_ = _Filter(class_name, (X,), {
        "__display__": class_name,
    })
    Filter_.__null__ = _null(X) if isinstance(_null(X), Filter_) else None
    return Filter_

@cache
def Compl(X: Type, *subtypes: Tuple_[Type]) -> Type:
    """
    Build the 'complement subtype' of a type by given subtypes:
        > an object 'x' of Compl(X, *subtypes)
        > is an 'x in X' such that 'is is not in Y'
        > for every 'Y in subtypes' if 'Y is subclass of X'
    """
    if not isinstance(X, type):
        raise TypeError(
            "Wrong type in Compl factory: \n"
            f" ==> '{_name(X)}': has unexpected type\n"
             "     [expected_type] TYPE"
            f"     [received_type] {_name(type(X))}"
        )
    unique_subtypes = tuple(set(subtypes))

    mistake_subtypes = []
    for subtype in unique_subtypes:
        if not isinstance(subtype, type):
            raise TypeError(
                "Wrong type in Compl factory: \n"
                f" ==> {_name(subtype)}: has unexpected type\n"
                 "     [expected_type] Typed"
                f"     [received_type] {_name(type(subtype))}"
            )
        if not issubclass(subtype, X):
            raise TypeError(
                "Wrong type in Compl factory: \n"
                f" ==> {_name(subtype)}: has unexpected type\n"
                f"     [expected_type] a subtype of {_name(X)}"
                f"     [received_type] {_name(type(subtype))}"
            )

    class_name = f"Compl({_name(X)}; {_name_list(*subtypes)})"

    class _Compl(type(X)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, cls.__base_type__):
                return False
            return not any(isinstance(instance, subtype) for subtype in cls.__excluded_subtypes__)

    Compl_ = _Compl(class_name, (X,), {
        "__display__": class_name,
        '__base_type__': X,
        '__excluded_subtypes__': unique_subtypes
    })
    Compl_.__null__ = _null(X) if isinstance(_null(X), Compl_) else None
    return Compl_

@cache
def Regex(regex: str) -> Type[str]:
    """
    Build the 'regex type' for a given regex:
        > an object 'x' of Regex(r'some_regex') is a string
        > that matches the regex r'some_regex'
    """

    from typed.mods.types.meta import _Pattern
    if not isinstance(regex, _Pattern("Pattern", (), {})):
        raise TypeError(
            "Wrong type in Regex factory: \n"
            f" ==> {regex}: has unexpected type\n"
             "     [expected_type] Pattern"
            f"     [received_type] {_name(type(regex))}"
        )

    from typed.mods.types.base import Str
    class _Regex(type(Str)):
        def __new__(cls, name, bases, dct):
            dct['_regex_pattern'] = re.compile(regex)
            dct['_regex'] = regex
            return super().__new__(cls, name, bases, dct)

        def __instancecheck__(cls, instance):
            x = re.compile(regex)
            return isinstance(instance, str) and x.match(instance) is not None

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, str)

    class_name = f"Regex({regex})"
    Regex_ = _Regex(class_name, (Str,), {
        "__display__": class_name,
    })
    Regex_.__null__ = "" if isinstance("", Regex_) else None
    return Regex_

@cache
def Range(x: int, y: int) -> Type[int]:
    """
    Build the 'range type' for a given integer range [x, y]:
        > an object 'z' of Range(x, y) is an integer
        > such that x <= z <= y
    """
    from typed.mods.types.base import Int
    if not isinstance(x, Int):
        raise TypeError(
            "Wrong type in Range factory: \n"
            f" ==> {x}: has unexpected type\n"
             "     [expected_type] Int\n"
            f"     [received_type] {_name(type(x))}"
        )
    if not isinstance(y, Int):
        raise TypeError(
            "Wrong type in Range factory: \n"
            f" ==> {y}: has unexpected type\n"
             "     [expected_type] Int\n"
            f"     [received_type] {_name(type(y))}"
        )

    class _Range(type(Int)):
        def __new__(cls, name, bases, dct, lower_bound, upper_bound):
            dct['_lower_bound'] = lower_bound
            dct['_upper_bound'] = upper_bound
            return super().__new__(cls, name, bases, dct)

        def __instancecheck__(cls, instance):
            return isinstance(instance, Int) and cls._lower_bound <= instance <= cls._upper_bound

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, Int)

    class_name = f"Range({x}, {y})"
    return _Range(class_name, (Int,), {
        "__display__": class_name,
        "__null__": x
    }, lower_bound=x, upper_bound=y)

@cache
def Not(*types: Tuple_[Type]) -> Type:
    """
    Build the 'not-type':
        > an object x of Not(X, Y, ...)
        > is NOT an instance of any X, Y, ...
    """
    from typed.mods.types.base import Any, Nill

    if not types:
        return Any
    if Any in types:
        return Nill

    class _Not(type):
        def __instancecheck__(cls, instance):
            return not any(isinstance(instance, typ) for typ in cls.__types__)

        def __subclasscheck__(cls, subclass):
            return not any(issubclass(subclass, typ) for typ in cls.__types__)

    class_name = f"Not({_name_list(*types)})"
    return _Not(class_name, (), {
        "__display__": class_name,
        '__types__': types,
        '__null__': None
    })

@cache
def Enum(typ: Type, *values: Tuple_[Any_]) -> Type:
    """
    Build the 'valued-type':
        > 'x' is an object of 'Enum(typ, *values)' iff:
            1. isinstance(x, typ) is True
            2. x in {v1, v2, ...}
        > Enum(typ, ...) is a subclass of 'typ'
        > Enum(typ) = Null(typ)
        > Enum() = Nill
    """
    if typ and not values:
        try:
            from typed.mods.factories.base import Null
            return Null(typ)
        except Exception as e:
            from typed.mods.types.base import Nill
            return Nill
    if typ and values:
        if not isinstance(typ, type):
            raise TypeError(
                "Wrong type in Enum factory: \n"
                f" ==> {_name(typ)}: has unexpected type\n"
                 "     [expected_type] Typed"
                f"     [received_type] {_name(type(typ))}"
            )
        for value in values:
            if not isinstance(value, typ):
                raise TypeError(
                    "Wrong type in Enum factory: \n"
                    f" ==> {value}: has unexpected type\n"
                    f"     [expected_type] {_name(typ)}"
                    f"     [received_type] {_name(type(value))}"
                )
    values_set = set(values)
    class _Enum(type(typ)):
        def __instancecheck__(cls, instance):
            return isinstance(instance, cls.__base_type__) and instance in cls.__allowed_values__

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, cls.__base_type__)

    class_name = f"Enum({_name(typ)}; {_name_list(*values)})"

    Enum_ = _Enum(class_name, (typ,), {
        "__display__": class_name,
        '__base_type__': typ,
        '__allowed_values__': values_set,
    })

    Enum_.__null__ = _null(typ) if isinstance(_null(typ), Enum_) else None
    return Enum_

@cache
def Single(x: Any_) -> Type:
    """
    Build the 'singleton-type':
        > the only object of 'Single(x)' is 'x'
        > 'Single(x)' is a subclass of 'type(x)'
    """
    t = type(x)

    class _Single(type(t)):
        def __instancecheck__(cls, instance):
            return type(instance) is t and instance == cls.__value__

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, t)

    class_name = f"Single({_name(x)})"
    return _Single(class_name, (t,), {
        "__display__": class_name,
        '__value__': x,
        '__null__': x
    })
Singleton = Single

@cache
def Len(typ: Type, size: int) -> Type:
    """
    Build a 'sized-type'.
        > An object of 'Len(X, size)' is an object
        > 'x' of 'X such that 'len(x) == size'.
        1. Valid only for sized types and size >= 0
        2. 'Len(typ, 0)' is 'Null(typ)'
    """
    if not isinstance(typ, type):
        raise TypeError(
            "Wrong type in Len factory: \n"
            f" ==> {typ}: has unexpected type\n"
            f"     [expected_type] TYPE"
            f"     [received_type] {_name(type(typ))}"
        )
    from typed.mods.types.attr import SIZED
    if not isinstance(typ, SIZED):
        raise TypeError(
            "Wrong type in Len factory: \n"
            f" ==> {typ}: has unexpected type\n"
            f"     [expected_type] TYPE"
            f"     [received_type] {_name(type(typ))}"
        )
    if not isinstance(size, int):
        raise TypeError(
            "Wrong type in Len factory: \n"
            f" ==> {size}: has unexpected type\n"
            f"     [expected_type] Nat"
            f"     [received_type] {_name(type(size))}"
        )
    if size < 0:
        raise TypeError(
            "Wrong type in Enum factory: \n"
            f" ==> {size}: has unexpected type\n"
            f"     [expected_type] Nat"
            f"     [received_type] {_name(type(size))}"
        )
    if size == 0:
        from typed.mods.types.base import Null
        return Null(typ)

    class _Len(type(typ)):
        def __instancecheck__(cls, instance):
            return isinstance(instance, typ) and len(instance) == cls.__len__

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, typ)

    class_name = f"Len({_name(typ)}; {size})"
    return _Len(class_name, (typ,), {
        "__display__": class_name,
        '__len__': size,
        '__null__': _null(typ) if size == 0 else None
    })

@cache
def Maybe(*types: Tuple_[Type]) -> Type:
    """
    Build a 'maybe-type'.
        > An object of `Maybe(X, Y, ..)`
        > is `None` or an object of `X`, `Y`, ...
    """
    from typed.mods.factories.base import Union
    Maybe_ = Union(*types, type(None))
    Maybe_.__display__ = f"Maybe({_name_list(*types)})"
    Maybe_.__null__ = _null_from_list(*types)
    return Maybe_

@cache
def SUBTYPES(*types: Tuple_[Type]) -> Type:
    """
    Build the type of subtypes of a given types.
        > An object of `SUBTYPE(X, Y, ...)`
        > is a type T such that issubclass(T, K) is True
        > for some K in (X, Y, ...)
    """
    for typ in types:
        if type(typ) is not type:
            raise TypeError(
                "Wrong type in SUBTYPES factory: \n"
                f" ==> {_name(typ)}: has unexpected type\n"
                f"     [expected_type] TYPE"
                f"     [received_type] {_name(type(typ))}"
            )

    class _SUBTYPES(type):
        def __instancecheck__(cls, instance):
            return any(issubclass(instance, typ) for typ in types)

    class_name = f"Sub({_name(*types)})"
    return _SUBTYPES(class_name, (), {
        "__display__": class_name,
        "__null__": None
    })
SUB = SUBTYPES

def Null(typ: Type) -> Type:
    if not isinstance(typ, type):
        raise TypeError(
            "Wrong type in 'Null' factory: \n"
            f" ==> '{_name(typ)}': has unexpected type\n"
             "     [expected_type] TYPE"
            f"     [received_type] {_name(type(typ))}"
        )
    if typ is type(None):
        return None

    if _null(typ) is None:
        raise TypeError(
            "Wrong type in 'Null' factory: \n"
            f" ==> '{_name(typ)}': has unexpected type\n"
             "     [expected_type] a type for which 'null(typ)' is defined"
            f"     [received_type] {_name(type(typ))}"
        )

    class _Null(type(typ)):
        def __instancecheck__(cls, instance):
            return instance == _null(typ)
        def __repr__(cls):
            return f"<Null({_name(typ)})>"

    class_name = f"Null({_name(typ)})"
    return _Null(class_name, (typ,), {
        "__display__": class_name,
        "__null__": _null(typ)
    })
