from functools import wraps
from typed.mods.types.builtin import *
from typed.mods.types.func    import *
from typed.mods.types.struc   import *
from typed.mods.ops.generics  import *
from typed.mods.ops.base      import *
from typed.mods.ops.func      import *

def typed(func):
    """Decorator that wraps a function with the appropriate TypedFuncType subclass."""
    sig = inspect.signature(func)
    return_annotation = sig.return_annotation
    wrapped_func = TypedFuncType(func)
    try:
        wrapped_func = BoolFuncType(func)
    except TypeError:
        pass
    return wraps(func)(wrapped_func)
