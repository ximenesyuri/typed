from typing import Tuple, Type
from types import FunctionType
from typed.mods.types_ import BoolFuncType
from typed.mods.helper import (
    __hinted_domain,
    __hinted_codomain
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

def Filter(X: Type, *funcs: Tuple[BoolFuncType]) -> Type:
    """
    Build the 'filtered subtype' of a given type with filter
    given by a tuple of boolean functions 'f in funcs' such
    that 'X is subclass of dom(f)'.
        > The objects of 'Filter(X, *funcs)' are objects
        > 'x in X' such that
            1. 'f(x) is True' for all 'f in funcs'.
    """
    if not isinstance(X, type):
        raise TypeError("Argument 'X' must be a type.")

    validated_funcs = []
    for i, f in enumerate(funcs):
        if not isinstance(f, BoolFuncType):
            raise TypeError(f"Argument at index {i+1} must be an instance of BoolFuncType.")
        domain_hints = __hinted_domain(f)

        if len(domain_hints) != 1:
            raise TypeError(f"BoolFunc at index {i} ('{getattr(f, '__name__', 'anonymous')}') must accept exactly one argument (domain hint).")

        func_domain_type = domain_hints[0]
        if not (isinstance(func_domain_type, type) and issubclass(X, func_domain_type)):
            raise TypeError(
                f"BoolFunc at index {i} ('{getattr(f, '__name__', 'anonymous')}') "
                f"has domain hint '{getattr(func_domain_type, '__name__', str(func_domain_type))}' "
                f"which is not a superclass of '{X.__name__}'."
            )

        validated_funcs.append(f)

    class __Filter(X):
        @classmethod
        def __instancecheck__(cls, instance):
            if not isinstance(instance, cls.__base__):
                return False
            try:
                return all(bool_func(instance) for bool_func in cls.__filters__)
            except Exception:
                return False

    sub_class_name = f"Filter({X.__name__}"
    if validated_funcs:
        sub_class_name += f", where {', '.join(getattr(f, '__name__', 'anonymous') for f in validated_funcs)})"
    else:
        sub_class_name += ")"

    return type(sub_class_name, (__Filter,), {'__filters__': tuple(validated_funcs)})

def Compl(X: Type, *subtypes: Tuple[Type]) -> Type:
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

    return __Compl(class_name, (object,), {'__base_type__': X, '__excluded_subtypes__': unique_subtypes})
