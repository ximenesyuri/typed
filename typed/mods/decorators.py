from typed.mods.types.base import TYPE
from functools import wraps, lru_cache
from inspect import isfunction

def typed(arg):
    """Decorator that wraps a function with the appropriate Typed subclass."""
    if isinstance(arg, type):
        return _variable_checker(arg)
    elif isfunction(arg):
        from typed.mods.types.base import Bool
        from typed.mods.types.func import Typed, Condition
        if isinstance(arg, Typed):
            return arg
        typed_arg = Typed(arg)
        dom = typed_arg.dom
        cod = typed_arg.cod
        if cod is Bool:
            typed_arg.__class__ = Condition
        else:
            typed_arg.__class__ = Typed(*dom, cod=cod) if cod else Typed(*dom)
        return typed_arg
    raise TypeError(
        "typed function can only be applied to types or callable objects:\n"
        f" ==> '{arg}': is not callable nor a type\n"
        f"     [received_type] '{type(arg).__name__}'"
    )

def condition(arg):
    """Decorator that wraps a function with the appropriate Typed subclass."""
    if isfunction(arg):
        from typed.mods.types.func import Condition
        if isinstance(arg, Condition):
            return arg
        cond = Condition(arg)
        cond.__class__ = Condition
        return cond
    raise TypeError(
        "typed function can only be applied to types or callable objects:\n"
        f" ==> '{arg}': is not callable nor a type\n"
        f"     [received_type] '{type(arg).__name__}'"
    )

def factory(arg):
    """Decorator that creates a factory with cache"""
    if isfunction(arg):
        typed_arg = typed(arg)
        if not issubclass(typed_arg.codomain, TYPE):
            raise TypeError(
                "Factories should create types:\n"
                f" ==> '{arg.__name__}' codomain is not a type\n"
                f"     [received_type]: '{typed_arg.codomain.__name__}'"
            )
        wrapped_func = lru_cache(maxsize=None)(typed(arg))
        return wraps(arg)(wrapped_func)
    raise TypeError(
        "Factory decorator can only be applied to callable objects:\n"
        f" ==> '{arg.__name__}': is not callable\n"
        f"     [received_type] '{type(arg).__name__}'"
    )
