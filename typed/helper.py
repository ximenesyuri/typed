from typed.mods.decorators import typed
from typed.mods.meta.base import _TYPE_
from typed.mods.types.base import Any, TYPE, Str, ITER

@typed
def typeof(obj: Any) -> TYPE:
    return TYPE(obj)

def declare(name, value=None):
    globals()[name] = value

@typed
def name(obj: Any) -> Str:
    from typed.mods.helper.helper import _name
    return _name(obj)

def Meta(name, bases, instancecheck, subclasscheck=None, **attrs):
    dct = {'__instancecheck__': staticmethod(instancecheck)}
    if subclasscheck:
        dct['__subclasscheck__'] = staticmethod(subclasscheck)
    dct.update(attrs)
    return type(name, bases, dct)

def Type(name, bases, instancecheck, subclasscheck=None, **attrs):
    meta_bases = tuple(TYPE(t) for t in bases)

    return Meta(name.upper(), meta_bases, instancecheck, subclasscheck)(name, bases, attrs)

@typed
def Generate(iter: ITER) -> TYPE:
    class TEST(_TYPE_):
        def __instancecheck__(cls, instance):
            return any(instance is x for x in iter)

        def __iter__(cls):
            return X.__iter__(cls)

    return TEST("test(X)", (), {})

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
