from typed.mods.decorators import typed
from typed.mods.types.base import Any, TYPE, Str
from typed.mods.helper.helper import _name

@typed
def typeof(obj: Any) -> TYPE:
    return TYPE(obj)

def declare(name, value=None):
    globals()[name] = value

@typed
def name(obj: Any) -> Str:
    return _name(obj)

def symmetrize(func=None, *, key=None):
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
