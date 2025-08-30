from typed.mods.types.base import TYPE
from typed.mods.types.func import Function
from functools import wraps, lru_cache
from typed.mods.helper.helper import _name

def typed(arg):
    """Decorator that creates a 'typed function' or a 'typed var'."""
    if isinstance(arg, TYPE):
        return _variable_checker(arg)
    elif isinstance(arg, Function):
        from typed.mods.helper.helper import _dependent_signature
        from typed.mods.types.base import Bool
        from typed.mods.types.func import Typed, Condition
        _dependent_signature(arg)
        if isinstance(arg, Typed):
            return arg
        typed_arg = Typed(arg)
        dom = typed_arg.dom
        cod = typed_arg.cod
        if cod is Bool:
            typed_arg.__class__ = Condition
        else:
            typed_arg.__class__ = Typed
        return typed_arg
    raise TypeError(
        "Wrong type in 'typed' decorator\n"
        f" ==> '{arg}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function' or of 'TYPE'\n"
        f"     [received_type] '{_name(TYPE(arg))}'"
    )

def condition(func):
    """Decorator that creates a 'condition', a.k.a 'predicate'"""
    if isinstance(func, Function):
        from typed.mods.types.func import Condition
        if isinstance(func, Condition):
            return func
        cond = Condition(func)
        cond.__class__ = Condition
        return cond
    raise TypeError(
        "Wrong type in 'condition' decorator\n"
        f" ==> '{func}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )
predicate = condition

def factory(func):
    """Decorator that creates a factory with cache"""
    if isfunction(func):
        typed_func = typed(func)
        if not issubclass(typed_func.codomain, TYPE):
            raise TypeError(
                "Factories should create types:\n"
                f" ==> '{_name(func)}': has codomain which is not a type\n"
                 "     [expected_type] TYPE\n"
                f"     [received_type]: '{_name(typed_func.codomain)}'"
            )
        wrapped_func = lru_cache(maxsize=None)(typed_func)
        return wraps(func)(wrapped_func)
    raise TypeError(
        "Wrong type in 'factory' decorator\n"
        f" ==> '{func}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )

def dependent(func):
    if isinstance(func, Function):
        typed_func = typed(func)
        if not issubclass(typed_func.codomain, TYPE):
            raise TypeError(
                "Factories should create types:\n"
                f" ==> '{_name(func)}': has codomain which is not a type\n"
                 "     [expected_type] TYPE\n"
                f"     [received_type]: '{_name(typed_func.codomain)}'"
            )
        typed_func._is_dependent_type = True
        typed_func._dependent_func = func
        return typed_func
    raise TypeError(
        "Wrong type in 'dependent' decorator\n"
        f" ==> '{func}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )
