from functools import wraps
from typed.mods.types_       import *
from typed.mods.ops.generics import *
from typed.mods.ops.base     import *
from typed.mods.ops.func     import *

def typed(func):
    """Decorator that wraps a function with TypedFuncType."""
    wrapped_func = TypedFuncType(func)
    return wraps(func)(wrapped_func)
