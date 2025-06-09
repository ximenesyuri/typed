from functools import wraps
from typed.mods.helper import _nill
from typed.mods.types.base          import *
from typed.mods.types.func          import *
from typed.mods.types.attr          import *
from typed.mods.factories.generics  import *
from typed.mods.factories.base      import *
from typed.mods.factories.func      import *

def typed(func):
    """Decorator that wraps a function with the appropriate TypedFuncType subclass."""
    wrapped_func = TypedFuncType(func)
    try:
        wrapped_func = BoolFuncType(func)
    except TypeError:
        pass
    return wraps(func)(wrapped_func)

# the null typed function
nill = typed(_nill)
