from typed.mods.types.base import TYPE
from typed.mods.types.func import Function
from functools import lru_cache, update_wrapper
from typed.mods.helper.helper import (
    _name,
    _has_dependent_type,
    _dependent_signature,
    _check_defaults_match_hints,
    _instrument_locals_check,
)

def hinted(func):
    if isinstance(func, Function):
        from typed.mods.types.func import Hinted
        if isinstance(func, Hinted):
            return func
        hinted_func = Hinted(func)
        hinted_func.__class__ = Hinted
        return hinted_func
    raise TypeError(
        "Wrong type in 'hinted' decorator\n"
        f" ==> '{_name(func)}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )

def typed(arg=None, *, defaults=False, cache=False, locals=False, rigid=False, dependent=False, lazy=True):
    from typed.mods.err import TypedErr

    def _build_typed(res_func):
        if getattr(res_func, "__lazy_typed__", False):
            res_func = res_func._orig

        if _has_dependent_type(res_func):
            if not dependent:
                raise TypeError(
                    f"Function '{res_func.__name__}' uses dependent types, "
                    f"but 'dependent=True' was not specified in @typed()"
                )
            _dependent_signature(res_func)

        if defaults or rigid:
            _check_defaults_match_hints(res_func)

        if locals or rigid:
            res_func = _instrument_locals_check(res_func, force_all_annotated=rigid)

        try:
            from typed.mods.types.base import Bool
            from typed.mods.types.func import Typed, Condition

            if isinstance(res_func, Typed):
                typed_func = res_func
            else:
                typed_func = Typed(res_func)

            cod = typed_func.cod
            if cod is Bool:
                typed_func.__class__ = Condition
            else:
                typed_func.__class__ = Typed

            res_func = typed_func
        except Exception as e:
            raise TypedErr(f"Error in the typed function '{_name(res_func)}':\n {e}")

        if cache:
            res_func = lru_cache(maxsize=None)(res_func)

        return res_func

    def _make_lazy_wrapper(func):
        from typed.mods.types.func import Typed

        class LazyTyped(Typed):
            __lazy_typed__ = True

            def __init__(self, f):
                self._orig = f
                self._wrapped = None
                self.func = f
                update_wrapper(self, f)

            def _materialize(self):
                if self._wrapped is None:
                    self._wrapped = _build_typed(self._orig)
                return self._wrapped

            def __call__(self, *a, **kw):
                return self._materialize()(*a, **kw)

            def __getattr__(self, name):
                return getattr(self._materialize(), name)

            def __repr__(self):
                return f"<LazyTyped for {getattr(self._orig, '__name__', 'anonymous')}>"

        return type.__call__(LazyTyped, func)

    def typed_decorator(func):
        if not lazy:
            return _build_typed(func)
        return _make_lazy_wrapper(func)

    if arg is not None and (isinstance(arg, TYPE) or isinstance(arg, Function)):
        if callable(arg):
            return typed_decorator(arg)
        else:
            from typed.mods.helper.helper import _variable_checker
            return _variable_checker(arg)

    elif arg is not None and callable(arg):
        return typed_decorator(arg)

    elif arg is None:
        def wrapper(f):
            return typed_decorator(f)
        return wrapper

    else:
        raise TypeError(
            "Wrong type in 'typed' decorator\n"
            f" ==> '{_name(arg)}': has an unexpected type\n"
            "     [expected_type] subtype of 'Function' or of 'TYPE'\n"
            f"     [received_type] '{_name(TYPE(arg))}'"
        )

def condition(func):
    """Decorator that creates a 'condition', a.k.a 'predicate'"""
    if isinstance(func, Function):
        from typed.mods.types.func import Condition
        if isinstance(func, Condition):
            return func
        cond = Condition(func)
        cond.__class__ = Condition
        return cond
    raise TypeError(
        "Wrong type in 'condition' decorator\n"
        f" ==> '{func}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )
predicate = condition

def factory(func):
    """Decorator that creates a factory with cache"""
    if isinstance(func, Function):
        from typed.mods.types.func import Typed
        typed_func = Typed(func)
        if not issubclass(typed_func.codomain, TYPE):
            raise TypeError(
                "Factories should create types:\n"
                f" ==> '{_name(func)}': has codomain which is not a type\n"
                 "     [expected_type] TYPE\n"
                f"     [received_type]: '{_name(typed_func.codomain)}'"
            )
        wrapped_func = lru_cache(maxsize=None)(typed_func)
        class FactoryWrapper:
            def __init__(self, original):
                self._original = original

            def __call__(self, *a, **kw):
                return self._original(*a, **kw)
        return update_wrapper(FactoryWrapper(func), func)
    raise TypeError(
        "Wrong type in 'factory' decorator\n"
        f" ==> '{func}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )

def operation(func):
    if isinstance(func, Function):
        from typed.mods.types.base import Tuple
        from typed.mods.types.func import Operation, Typed
        typed_func = Typed(func)
        if not isinstance(typed_func.domain, Tuple(TYPE)):
            raise TypeError(
                "Operations should operate on types:\n"
                f" ==> '{_name(func)}': has domain which is not a tuple of types\n"
                 "     [expected_type] subtype of Tuple(TYPE)\n"
                f"     [received_type] '{_name(typed_func.domain)}'"
            )
        if not isinstance(typed_func.codomain, TYPE):
            raise TypeError(
                "Operations should return a type:\n"
                f" ==> '{_name(func)}': has codomain which is not a type\n"
                 "     [expected_type]  subtype of TYPE\n"
                f"     [received_type]: '{_name(typed_func.codomain)}'"
            )
        typed_func.__class__ = Operation
        return typed_func
    raise TypeError(
        "Wrong type in 'operation' decorator\n"
        f" ==> '{_name(func)}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )

def dependent(func):
    if isinstance(func, Function):
        from typed.mods.types.func import Dependent, Typed
        typed_func = Typed(func)
        if not issubclass(typed_func.codomain, TYPE):
            raise TypeError(
                "Factories should create types:\n"
                f" ==> '{_name(func)}': has codomain which is not a type\n"
                 "     [expected_type] TYPE\n"
                f"     [received_type]: '{_name(typed_func.codomain)}'"
            )
        typed_func.__class__ = Dependent
        typed_func.is_dependent_type = True
        typed_func.dependent_func = func
        return typed_func
    raise TypeError(
        "Wrong type in 'dependent' decorator\n"
        f" ==> '{_name(func)}': has an unexpected type\n"
         "     [expected_type] subtype of 'Function'\n"
        f"     [received_type] '{_name(TYPE(func))}'"
    )
