from typed.mods.types.func import Typed
from typed.mods.types.base import Condition, TYPE
from functools import wraps, lru_cache

def typed(arg):
    """Decorator that wraps a function with the appropriate Typed subclass."""
    if isinstance(arg, type):
        return _variable_checker(arg)
    elif callable(arg):
        wrapped_func = Typed(arg)
        try:
            wrapped_func = Condition(arg)
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

def symmetric(func=None, *, key=None):
    """
    Decorator that makes a function symmetric in its positional arguments:
      – All permutations of *args get sorted (by key or by value, or by repr())
        before you actually invoke the underlying function.
      – **kwargs are left untouched.
    """
    def _decorate(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if key is not None:
                try:
                    ordered = tuple(sorted(args, key=key))
                except Exception as e:
                    raise ValueError(f"symmetric: can't sort args with key={key!r}: {e}")
            else:
                try:
                    ordered = tuple(sorted(args))
                except TypeError:
                    ordered = tuple(sorted(args, key=lambda x: repr(x)))
            return f(*ordered, **kwargs)
        return wrapper
    if func is None:
        return _decorate
    else:
        return _decorate(func)
