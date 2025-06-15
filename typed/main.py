from functools import wraps
from typed.mods.helper import _variable_checker
from typed.mods.helper import _nill
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

# the null typed function
nill = typed(_nill)
