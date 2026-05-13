from typed.helper.poly import (
    _is_placeholder_like,
    _resolve_placeholder_value,
    _append,
    _join,
    _split,
    Checker
)

some = Checker(any)
every = Checker(all)

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
