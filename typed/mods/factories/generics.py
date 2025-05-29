import re
from typing import Tuple, Type
from typed.mods.types.func import BoolFuncType
from typed.mods.helper import (
    _hinted_domain,
    _hinted_codomain
)

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

    class __Inter(type):
        def __instancecheck__(cls, instance):
            return all(isinstance(instance, t) for t in cls.__types__)

    class_name = f"Inter({', '.join(t.__name__ for t in unique_types)})"

    return __Inter(class_name, (object,), {'__types__': unique_types})

def Filter(X, *funcs):
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

    class Meta(type(X)):
        def __instancecheck__(cls, instance):
            return all(f(instance) for f in real_filters) 

    return Meta(f"Filter({X.__name__})", (X,), {})


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

    class __Compl(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, cls.__base_type__):
                return False
            return not any(isinstance(instance, subtype) for subtype in cls.__excluded_subtypes__)

    return __Compl(class_name, (X,), {'__base_type__': X, '__excluded_subtypes__': unique_subtypes})

def Regex(regex_string: str) -> Type[str]:
    """
    Build the 'regex type' for a given regex:
        > an object 'x' of Regex(r'some_regex') is a string
        > that matches the regex r'some_regex'
    """
    if not isinstance(regex_string, str):
        raise TypeError("regex_string must be a string.")

    class __Regex(str):
        _regex_pattern = re.compile(regex_string)
        _regex_string = regex_string

        def __instancecheck__(cls, instance: str) -> bool:
            return isinstance(instance, str) and cls._regex_pattern.match(instance) is not None

        def __subclasscheck__(cls, subclass: Type) -> bool:
            return issubclass(subclass, str)

        def __repr__(self):
            return f"Regex(r'{self._regex_string}')"

        def __str__(self):
            return f"Regex(r'{self._regex_string}')"

    return type(f"Regex_{hash(regex_string)}", (__Regex,), {})
