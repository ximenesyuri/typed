from typed.mods.decorators import typed
from typed.mods.types.base import Any, TYPE, Str, Tuple, Dict, META, PARAMETRIC
from typed.mods.types.func import Function, Factory
from typed.mods.helper.helper import _name

@typed
def typeof(obj: Any) -> TYPE:
    return TYPE(obj)

def declare(name, value=None):
    globals()[name] = value

@typed
def name(obj: Any) -> Str:
    return _name(obj)

class new:
    @typed
    def meta(name: Str, meta_bases: Tuple(TYPE), instancecheck: Function, subclasscheck: Function=None) -> META:
        from typed.mods.helper.helper import _META
        return _META(name, meta_bases, instancecheck, subclasscheck)

    @typed
    def type(name: Str, meta_bases: Tuple(TYPE), instancecheck: Function, subclasscheck: Function=None, **attrs: Dict) -> TYPE:
        from typed.mods.types.base import Str
        if not isinstance(name, Str):
            raise TypeError
        meta_bases = tuple(TYPE(t) for t in bases)
        return _META(name.upper(), meta_bases, instancecheck, subclasscheck)(name, bases, attrs)

    @typed
    def parametric(*types: Tuple(TYPE), factory: Factory=None) -> PARAMETRIC:
        TYPES = (TYPE(typ) for typ in types)
        class _PARAMETRIC_(*TYPES):
            def __instancecheck__(cls, instance):
                return all(isinstance(instance, typ) for typ in types)
            def __subclasscheck__(cls, subclass):
                return all(issubclass(subclass, typ) for typ in types)
            def __call__(self, *args, **kwargs):
                if not args and not kwargs:
                    return self._type()
                elif args and isinstance(args[0], type):
                    return self._factory(*args, **kwargs)
                else:
                    return self._type(*args, **kwargs)

        class_name = _name(base_type)
        return _PARAMETRIC_(class_name, (base_type,), {
            "__display__": class_name,
            "base_type": base_type,
            "factory": factory
        })

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
