from typed.mods.types.base import TYPE
from typed.mods.types.func import Function
from functools import wraps, lru_cache
from typed.mods.helper.helper import _name

def hinted(func):
    if isinstance(func, Function):
        from typed.mods.types.func import Hinted
        if isinstance(func, Hinted):
            return func
        hinted_func = Hinted(func)
        hinted_func.__class__ = Hinted
        return hinted_func
    raise TypeError(
        "Wrong type in 'hinted' decorator\n"
        f" ==> '{_name(func)}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )

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
        f" ==> '{_name(arg)}': has an unexpected type\n"
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
    if isinstance(func, Function):
        from typed.mods.types.func import Factory, Typed
        typed_func = Typed(func)
        if not issubclass(typed_func.codomain, TYPE):
            raise TypeError(
                "Factories should create types:\n"
                f" ==> '{_name(func)}': has codomain which is not a type\n"
                 "     [expected_type] TYPE\n"
                f"     [received_type]: '{_name(typed_func.codomain)}'"
            )
        wrapped_func = lru_cache(maxsize=None)(typed_func)
        wrapped_func.__class__ = Factory
        return wraps(func)(wrapped_func)
    raise TypeError(
        "Wrong type in 'factory' decorator\n"
        f" ==> '{func}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )

def operation(func):
    if isinstance(func, Function):
        from typed.mods.types.base import Tuple
        from typed.mods.types.func import Operation, Typed
        typed_func = Typed(func)
        if not isinstance(typed_func.domain, Tuple(TYPE)):
            raise TypeError(
                "Operations should operate on types:\n"
                f" ==> '{_name(func)}': has domain which is not a tuple of types\n"
                 "     [expected_type] subtype of Tuple(TYPE)\n"
                f"     [received_type] '{_name(typed_func.domain)}'"
            )
        if not isinstance(typed_func.codomain, TYPE):
            raise TypeError(
                "Operations should return a type:\n"
                f" ==> '{_name(func)}': has codomain which is not a type\n"
                 "     [expected_type]  subtype of TYPE\n"
                f"     [received_type]: '{_name(typed_func.codomain)}'"
            )
        typed_func.__class__ = Operation
        return typed_func
    raise TypeError(
        "Wrong type in 'operation' decorator\n"
        f" ==> '{_name(func)}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )

def dependent(func):
    if isinstance(func, Function):
        from typed.mods.types.func import Dependent, Typed
        typed_func = Typed(func)
        if not issubclass(typed_func.codomain, TYPE):
            raise TypeError(
                "Factories should create types:\n"
                f" ==> '{_name(func)}': has codomain which is not a type\n"
                 "     [expected_type] TYPE\n"
                f"     [received_type]: '{_name(typed_func.codomain)}'"
            )
        typed_func.__class__ = Dependent
        typed_func.is_dependent_type = True
        typed_func.dependent_func = func
        return typed_func
    raise TypeError(
        "Wrong type in 'dependent' decorator\n"
        f" ==> '{_name(func)}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )
