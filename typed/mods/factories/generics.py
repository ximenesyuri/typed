import re
from functools import lru_cache as cache
from typing import Tuple as Tuple_, Type, Any as Any_
from types import FunctionType
from typed.mods.helper.helper import (
    _hinted_domain,
    _hinted_codomain,
    _name,
    _name_list,
    _null
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
                f" ==> {f}: has unexpected type\n"
                 "     [expected_type] TYPE"
                f"     [received_type] {_name(type(t))}"
            )
    unique_types = tuple(set(types))

    if len(unique_types) == 1:
        return unique_types[0]

    non_builtin_types = [t for t in unique_types if not t.__module__ == 'builtins']

    class _Inter(type):
        def __instancecheck__(cls, instance):
            return all(isinstance(instance, t) for t in non_builtin_types)

    class_name = f"Inter({_name_list(*unique_types)})"
    if non_builtin_types:
        return _Inter(class_name, (), {'__types__': unique_types})
    return type(None)

@cache
def Filter(X: Type, *funcs: Tuple_[FunctionType]) -> Type:
    real_filters = []
    from typed.mods.types.base import Any
    from typed.mods.types.base import Condition
    for f in funcs:
        if not isinstance(f, Condition):
            raise TypeError(
                "Wrong type in Filter factory: \n"
                f" ==> {f.__name__}: has unexpected type\n"
                 "     [expected_type] Condition"
                f"     [received_type] {_name(type(f))}"
            )
        domain_hints = _hinted_domain(f)
        if len(domain_hints) != 1:
            raise TypeError(
                "Wrong type in Filter factory: \n"
                f" ==> {f.__name__}: has unexpected type\n"
                 "     [expected_type] Condition(1)"
                f"     [received_type] {_name(type(f))}"
            )
        domain = domain_hints[0]
        if domain is Any:
            pass
        elif not issubclass(X, domain):
            raise TypeError(
                "Wrong type in Union factory: \n"
                f" ==> {X.__name__}: has unexpected type\n"
                 "     [expected_type] some subtype of 'dom(f)' for every 'f' in 'funcs'"
                f"     [received_type] {_name(type(X))}"
            )
        if hasattr(f, 'func'):
            real_filters.append(f.func)
        else:
            real_filters.append(f)

    class _Filter(type(X)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, X):
                return False
            return all(f(instance) for f in real_filters)

    class_name = f"Filter({_name(X)}; {_name_list(*funcs)})"
    return _Filter(class_name, (X,), {"__display__": class_name})

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
            f" ==> 'X': has unexpected type\n"
             "     [expected_type] TYPE"
            f"     [received_type] {_name(type(X))}"
        )
    unique_subtypes = tuple(set(subtypes))

    mistake_subtypes = []
    for subtype in unique_subtypes:
        if not isinstance(subtype, type):
            raise TypeError(
                "Wrong type in Compl factory: \n"
                f" ==> {subtype}: has unexpected type\n"
                 "     [expected_type] Typed"
                f"     [received_type] {_name(type(t))}"
            )
        if not issubclass(subtype, X):
            raise TypeError(
                "Wrong type in Compl factory: \n"
                f" ==> {subtype}: has unexpected type\n"
                 "     [expected_type] a subtype of X"
                f"     [received_type] {_name(type(subtype))}"
            )

    class_name = f"Compl({_name(X)}; {_name_list(*subtypes)})"

    class _Compl(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, cls.__base_type__):
                return False
            return not any(isinstance(instance, subtype) for subtype in cls.__excluded_subtypes__)

    return _Compl(class_name, (X,), {"__display__": class_name, '__base_type__': X, '__excluded_subtypes__': unique_subtypes})

@cache
def Regex(regex: str) -> Type[str]:
    """
    Build the 'regex type' for a given regex:
        > an object 'x' of Regex(r'some_regex') is a string
        > that matches the regex r'some_regex'
    """
    from typed.mods.types.base import Pattern
    if not isinstance(regex, Pattern):
        raise TypeError(
            "Wrong type in Regex factory: \n"
            f" ==> {regex}: has unexpected type\n"
             "     [expected_type] Pattern"
            f"     [received_type] {_name(type(regex))}"
        )

    class _Regex(type):
        def __new__(cls, name, bases, dct, regex_pattern):
            dct['_regex_pattern'] = re.compile(regex_pattern)
            dct['_regex'] = regex_pattern
            return super().__new__(cls, name, bases, dct)

        def __instancecheck__(cls, instance):
            return isinstance(instance, str) and cls._regex_pattern.match(instance) is not None

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, str)

    class_name = f"Regex({regex})"
    return _Regex(class_name, (str,), {"__display__": class_name}, regex_pattern=regex)

@cache
def Range(x: int, y: int) -> Type[int]:
    """
    Build the 'range type' for a given integer range [x, y]:
        > an object 'z' of Range(x, y) is an integer
        > such that x <= z <= y
    """
    if not isinstance(x, int):
        raise TypeError(
            "Wrong type in Range factory: \n"
            f" ==> {x}: has unexpected type\n"
             "     [expected_type] Int"
            f"     [received_type] {_name(type(x))}"
        )
    if not isinstance(y, int):
        raise TypeError(
            "Wrong type in Range factory: \n"
            f" ==> {y}: has unexpected type\n"
             "     [expected_type] Int"
            f"     [received_type] {_name(type(y))}"
        )

    class _Range(type):
        def __new__(cls, name, bases, dct, lower_bound, upper_bound):
            dct['_lower_bound'] = lower_bound
            dct['_upper_bound'] = upper_bound
            return super().__new__(cls, name, bases, dct)

        def __instancecheck__(cls, instance):
            return isinstance(instance, int) and cls._lower_bound <= instance <= cls._upper_bound

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, int)

    class_name = f"Range({x}, {y})"
    return _Range(class_name, (int,), {"__display__": class_name}, lower_bound=x, upper_bound=y)

@cache
def Not(*types: Tuple_[Type]) -> Type:
    """
    Build the 'not-type':
        > an object x of Not(X, Y, ...)
        > is NOT an instance of any X, Y, ...
    """
    from typed.mods.types.base import Any, Nill

    _flattypes, _ = _flat(*types)

    if not _flattypes:
        return Any
    if Any in _flattypes:
        return Nill

    class _Not(type):
        def __instancecheck__(cls, instance):
            return not any(isinstance(instance, typ) for typ in cls.__types__)

        def __subclasscheck__(cls, subclass):
            return not any(issubclass(subclass, typ) for typ in cls.__types__)

    class_name = f"Not({', '.join(t.__name__ for t in _flattypes)})"
    return _Not(class_name, (), {"__display__": class_name, '__types__': _flattypes})

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
                f" ==> {typ}: has unexpected type\n"
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
    class _Enum(type):
        def __instancecheck__(cls, instance):
            return isinstance(instance, cls.__base_type__) and instance in cls.__allowed_values__

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, cls.__base_type__)

    class_name = f"Enum({_name(typ)}; {_name_list(*values)})"
    return _Enum(class_name, (typ,), {
        "__display__": class_name,
        '__base_type__': typ,
        '__allowed_values__': values_set,
        "__null__": _null(typ)
    })

@cache
def Single(x: Any_) -> Type:
    """
    Build the 'singleton-type':
        > the only object of 'Single(x)' is 'x'
        > 'Single(x)' is a subclass of 'type(x)'
    """
    t = type(x)

    class _Single(type):
        def __instancecheck__(cls, instance):
            return type(instance) is t and instance == cls.__value__

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, t)

    class_name = f"Single({_name(x)})"
    return _Single(class_name, (t,), {"__display__": class_name, '__value__': x})
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
    return _Len(class_name, (typ,), {"__display__": class_name, '__len__': size})

@cache
def Maybe(*types: Tuple_[Type]) -> Type:
    """
    Build a 'maybe-type'.
        > An object of `Maybe(X, Y, ..)`
        > is `None` or an object of `X`, `Y`, ...
    """
    from typed.mods.factories.base import Union
    return Union(*types, type(None))

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
                f" ==> {typ}: has unexpected type\n"
                f"     [expected_type] TYPE"
                f"     [received_type] {_name(type(typ))}"
            )

    class _SUBTYPES(type):
        def __instancecheck__(cls, instance):
            return any(issubclass(instance, typ) for typ in types)

    class_name = f"Sub({_name(*types)})"
    return _SUBTYPES(class_name, (), {"__display__": class_name})
