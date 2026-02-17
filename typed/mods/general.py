from typed.mods.decorators import typed
from typed.mods.types.base import (
    Any, TYPE, Str, Tuple, Dict, META, PARAMETRIC
)
from typed.mods.types.func import Function, Factory
from typed.mods.helper.helper import _name, _name_list
from typed.mods.helper.null import _null
from typed.mods.helper.general import (
    Var,
    _is_placeholder_like,
    _resolve_placeholder_value,
    _append,
    _join,
    _split,
    Switch,
    Func
)

@typed
def name(obj: Any) -> Str:
    return _name(obj)

@typed
def names(*objs: Tuple) -> Str:
    return _name_list(*objs)

null = _null

var = Var()
_ = var

def switch(value):
    return Switch(value=value)

def func(*iterators, **vars):
    return Func(*iterators, **vars)

def append(container, *args, **kwargs):
    if any(
        _is_placeholder_like(x)
        for x in (container, *args, *kwargs.values())
    ):
        def func(*call_args, **call_kwargs):
            obj = _resolve_placeholder_value(container, call_args, call_kwargs)
            if obj is None:
                return None

            resolved_args = [
                _resolve_placeholder_value(a, call_args, call_kwargs)
                for a in args
            ]
            resolved_kwargs = {
                k: _resolve_placeholder_value(v, call_args, call_kwargs)
                for k, v in kwargs.items()
            }
            return _append(obj, *resolved_args, **resolved_kwargs)
        return func
    return _append(container, *args, **kwargs)

def join(*args):
    if any(_is_placeholder_like(a) for a in args):
        def func(*call_args, **call_kwargs):
            resolved = [
                _resolve_placeholder_value(a, call_args, call_kwargs)
                for a in args
            ]
            return _join(*resolved)
        return func
    return _join(*args)

def split(container, *args, **kwargs):
    if any(
        _is_placeholder_like(x)
        for x in (container, *args, *kwargs.values())
    ):
        def func(*call_args, **call_kwargs):
            obj = _resolve_placeholder_value(container, call_args, call_kwargs)
            if obj is None:
                return None

            resolved_args = [
                _resolve_placeholder_value(a, call_args, call_kwargs)
                for a in args
            ]
            resolved_kwargs = {
                k: _resolve_placeholder_value(v, call_args, call_kwargs)
                for k, v in kwargs.items()
            }
            return _split(obj, *resolved_args, **resolved_kwargs)
        return func

    return _split(container, *args, **kwargs)

class new:
    @typed
    def meta(name: Str, meta_bases: Tuple(TYPE), instancecheck: Function, subclasscheck: Function=None) -> META:
        from typed.mods.helper.helper import _META
        return _META(name, meta_bases, instancecheck, subclasscheck)

    @typed
    def type(name: Str, meta_bases: Tuple(TYPE), instancecheck: Function, subclasscheck: Function=None, **attrs: Dict) -> TYPE:
        from typed.mods.types.base import Str
        from typed.mods.helper.helper import _META
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

def poly(attr: str):
    def polymorphic_function(obj, *args, **kwargs):
        obj_type = type(obj)
        if not hasattr(obj_type, attr):
            raise AttributeError(f"type '{obj_type.__name__}' has no attribute '{attr}'")
        method = getattr(obj_type, attr)
        if not callable(method):
            raise TypeError(f"'{attr}' is not callable on type '{obj_type.__name__}'")
        return method(obj, *args, **kwargs)
    return polymorphic_function

convert = poly("__convert__")
