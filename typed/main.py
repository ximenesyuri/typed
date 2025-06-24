from functools import wraps, lru_cache
from typed.mods.helper.helper import _variable_checker, _nill, _get_null_object
from typed.mods.types.base          import *
from typed.mods.types.func          import *
from typed.mods.types.attr          import *
from typed.mods.factories.generics  import *
from typed.mods.factories.base      import *
from typed.mods.factories.func      import *

def typed(arg):
    """Decorator that wraps a function with the appropriate TypedFuncType subclass."""
    if isinstance(arg, type):
        return _variable_checker(arg)
    elif callable(arg):
        wrapped_func = TypedFuncType(arg)
        try:
            wrapped_func = BoolFuncType(arg)
        except TypeError:
            pass
        return wraps(arg)(wrapped_func)
    raise TypeError(
        "typed function can only be applied to types or callable objects:\n"
        f" ==> '{arg}': is not callable nor a type\n"
        f"     [received_type] '{type(arg).__name__}'"
    )

def factory(arg):
    """Decorator that creates a factory with cache"""
    if callable(arg):
        typed_arg = typed(arg)
        if not issubclass(typed_arg.codomain, Type):
            raise TypeError(
                "Factories should create types:\n"
                f" ==> '{arg.__name__}' codomain is not a type\n"
                f"     [received_type]: '{typed_arg.codomain.__name__}'"
            )
        return lru_cache(maxsize=None)(typed(arg))
        return wraps(arg)(wrapped_func)
    raise TypeError(
        "Factory decorator can only be applied to callable objects:\n"
        f" ==> '{arg}': is not callable\n"
        f"     [received_type] '{type(arg).__name__}'"
    )

# the null typed function
nill = typed(_nill)

# the null values
null = _get_null_object

# instance and subtype checking
subtype = issubclass
belongs = isinstance
