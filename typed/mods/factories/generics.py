import re
from functools import lru_cache as cache
from typing import Tuple, Type, Any as Any_
from typed.mods.types.func import BoolFuncType
from typed.mods.helper.helper import (
    _flat,
    _hinted_domain,
    _hinted_codomain
)

@cache
def Inter(*types: Tuple[Type]) -> Type:
    """
    Build the 'intersection' of types:
        > an object 'p' of the Inter(X, Y, ...)
        > is an object of every 'X, Y, ...'
    OBS: not applied to builtin types
    """
    unique_types = tuple(set(types))

    if not unique_types:
        return object
    if len(unique_types) == 1:
        return unique_types[0]

    if any(not isinstance(t, type) for t in unique_types):
        raise TypeError("All arguments must be types.")

    if any(t.__module__ == 'builtins' and t is not object for t in unique_types):
        raise TypeError("Cannot create an intersection type with specific built-in types due to potential layout conflicts.")

    class _Inter(type):
        def __instancecheck__(cls, instance):
            return all(isinstance(instance, t) for t in cls.__types__)

    class_name = f"Inter({', '.join(t.__name__ for t in unique_types)})"

    return _Inter(class_name, (object,), {'__types__': unique_types})

@cache
def Filter(X: Type, *funcs: Tuple[BoolFuncType]) -> Type:
    real_filters = []
    from typed.mods.types.base import Any
    for f in funcs:
        if not isinstance(f, BoolFuncType):
            raise TypeError(f"The function '{f.__name__}' is not of type BoolFuncType.")
        domain_hints = _hinted_domain(f)
        if len(domain_hints) != 1:
            raise TypeError(f"Function '{f.__name__}' must take one argument.")
        func_domain_type = domain_hints[0]
        if func_domain_type is Any:
            pass
        elif not issubclass(X, func_domain_type):
            raise TypeError(
                f"BoolFunc '{getattr(f, '__name__', 'anonymous')}' "
                f"has domain hint '{getattr(func_domain_type, '__name__', str(func_domain_type))}' "
                f"which is not a superclass of '{X.__name__}'."
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

    return _Filter(f"Filter({X.__name__})", (X,), {})

@cache
def Compl(X: Type, *subtypes: Tuple[Type]) -> Type:
    """
    Build the 'complement subtype' of a type by given subtypes:
        > an object 'x' of Compl(X, *subtypes)
        > is an 'x in X' such that 'is is not in Y'
        > for every 'Y in subtypes' if 'Y is subclass of X'
    """
    if not isinstance(X, type):
        raise TypeError(f"Argument 'X' must be a type, but got '{X.__name__}'.")
    unique_subtypes = tuple(set(subtypes))

    mistake_subtypes = []
    for subtype in unique_subtypes:
        if not isinstance(subtype, type):
            raise TypeError(f"'{subtype}' is not a type.")
        if not issubclass(subtype, X):
            mistake_subtypes.append(subtype)

    if mistake_subtypes:
        raise TypeError(f"The types {', '.join(t.__name__ for t in mistake_subtypes)} are not subtypes of '{X.__name__}'.")

    class_name = f"Compl({X.__name__}"
    if unique_subtypes:
       class_name += f" excluding {', '.join(sub.__name__ for sub in unique_subtypes)})"
    else:
       class_name += ")"

    class _Compl(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, cls.__base_type__):
                return False
            return not any(isinstance(instance, subtype) for subtype in cls.__excluded_subtypes__)

    return _Compl(class_name, (X,), {'__base_type__': X, '__excluded_subtypes__': unique_subtypes})

@cache
def Regex(regex_string: str) -> Type[str]:
    """
    Build the 'regex type' for a given regex:
        > an object 'x' of Regex(r'some_regex') is a string
        > that matches the regex r'some_regex'
    """
    from typed.mods.types.base import Pattern
    if not isinstance(regex_string, Pattern):
        raise TypeError(f"'{regex_string}' is not a valid pattern.")

    class _Regex(type):
        def __new__(cls, name, bases, dct, regex_pattern):
            dct['_regex_pattern'] = re.compile(regex_pattern)
            dct['_regex_string'] = regex_pattern
            return super().__new__(cls, name, bases, dct)

        def __instancecheck__(cls, instance: str) -> bool:
            return isinstance(instance, str) and cls._regex_pattern.match(instance) is not None

        def __subclasscheck__(cls, subclass: Type) -> bool:
            return issubclass(subclass, str)

    class_name = f"Regex({regex_string})"
    return _Regex(class_name, (str,), {}, regex_pattern=regex_string)

@cache
def Range(x: int, y: int) -> Type[int]:
    """
    Build the 'range type' for a given integer range [x, y]:
        > an object 'z' of Range(x, y) is an integer
        > such that x <= z <= y
    """
    if not isinstance(x, int):
        raise TypeError("x must be an integer.")
    if not isinstance(y, int):
        raise TypeError("y must be an integer.")

    class _Range(type):
        def __new__(cls, name, bases, dct, lower_bound, upper_bound):
            dct['_lower_bound'] = lower_bound
            dct['_upper_bound'] = upper_bound
            return super().__new__(cls, name, bases, dct)

        def __instancecheck__(cls, instance: int) -> bool:
            return isinstance(instance, int) and cls._lower_bound <= instance <= cls._upper_bound

        def __subclasscheck__(cls, subclass: Type) -> bool:
            return issubclass(subclass, int)
    class_name = f"Range({x}, {y})"
    return _Range(class_name, (int,), {}, lower_bound=x, upper_bound=y)

@cache
def Not(*types: Tuple[Type]) -> Type:
    """
    Build the 'not'-type:
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
    return _Not(class_name, (), {'__types__': _flattypes})

@cache
def Values(typ: Type, *values: Tuple[Any_]) -> Type:
    """
    Build the 'valued-type':
        > 'x' is an object of 'Values(typ, *values)' iff:
            1. isinstance(x, typ) is True
            2. x in {v1, v2, ...}
        > Values(typ, ...) is a subclass of 'typ'
    """
    values_set = set(values)
    class_name = "Values({} : {})".format(getattr(typ, '__name__', repr(typ)),
                                          ", ".join(repr(v) for v in values))
    class _Values(type):
        def __instancecheck__(cls, instance):
            for value in values:
                if not type(value) is typ:
                    raise TypeError(
                        f"Type mismatch for value '{value}':" +
                        f"\n\t[received_type]: '{type(value).__name__}'" +
                        f"\n\t[expected_type]: '{typ.__name__}'"
                    )

            return isinstance(instance, cls.__base_type__) and instance in cls.__allowed_values__

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, cls.__base_type__)

    return _Values(class_name, (typ,), {
        '__base_type__': typ,
        '__allowed_values__': values_set
    })

@cache
def Single(x: Any_) -> Type:
    """
    Build the 'singleton-type':
        > the only object of 'Single(x)' is 'x'
        > 'Is(x)' is a subclass of 'type(x)'
    """
    t = type(x)
    class_name = f"Single({repr(x)})"

    class _Single(type):
        def __instancecheck__(cls, instance):
            return type(instance) is t and instance == cls.__the_value__

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, t)

    return _Single(class_name, (t,), {'__the_value__': x})

@cache
def Len(typ: Type, size: int) -> Type:
    """
    Build a 'sized-type'.
        > An object of 'Len(X, size)' is an object
        > 'x' of 'X such that 'len(x) == size'.
        1. Valid only for sized types and size >= 0
        2. 'Len(typ, 0)' is 'Null(typ)'
    """
    if not isinstance(size, int):
        raise TypeError(
            f"'size': Type mismatch." +
            f"\n\t[received_value]: '{size}'"
            f"\n\t [received_type]: '{type(size).__name__}'"
            f"\n\t [expected_value]: 'int'"
        )
    if size < 0:
        raise ValueError(
            f"'size': invalid value" +
            f"\n\t[received_value]: '{size}'"
            f"\n\t[expected_value]: 'a nonnegative integer"
        )
    if size == 0:
        from typed.mods.types.base import Null
        return Null(typ)

    from typed.mods.types.attr import Sized
    if not isinstance(typ, type) or not isinstance(typ, Sized):
        raise TypeError(f"Len: type {typ!r} is not Sized.")

    class _Len(type(typ)):
        def __instancecheck__(cls, instance):
            return isinstance(instance, typ) and len(instance) == cls.__len__
        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, typ)

    class_name = f"Len({getattr(typ, '__name__', str(typ))}, {size})"
    return _Len(class_name, (typ,), {'__len__': size})

@cache
def Maybe(*types: Tuple[Type]) -> Type:
    """
    Build a 'maybe-type'.
        > An object of `Maybe(X, Y, ..)`
        > is `None` or an object of `X`, `Y`, ...
    """
    from typed.mods.factories.base import Union
    return Union(*types, type(None))

@cache
def SUB(*types: Tuple[Type]) -> Type:
    """
    Build the type of subtypes of a given types.
        > An object of `Type(X, Y, ...)`
        > is a type T such that issubclass(T, K) is True
        > for some K in (X, Y, ...)
    """
    class _Sub(type):
        def __instancecheck__(cls, instance):
            return isinstance(instance, type) and any(issubclass(instance, typ) for typ in types)

    class_name = f"Sub({', '.join(t.__name__ for t in types)})"
    return _Sub(class_name, (), {})

