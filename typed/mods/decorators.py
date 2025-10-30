from typed.mods.types.base import TYPE
from typed.mods.types.func import Function
from functools import lru_cache, update_wrapper
from typed.mods.helper.helper import _name, _has_dependent_type, _dependent_signature, _check_defaults_match_hints, _instrument_locals_check, _variable_checker
from typed.mods.err import TypedErr

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

def typed(arg=None, *, defaults=False, cache=False, locals=False, full=False, dependent=False):
    """
    Decorator that creates a 'typed function' or 'typed var'.
    Allows: @typed, @typed(defaults=.., cache=.., locals=.., full=.., dependent=..)
    """
    def typed_decorator(func):
        res_func = func

        # --- 0. If dependent=False, disallow dependent types
        if _has_dependent_type(res_func):
            if not dependent:
                raise TypeError(
                    f"Function '{func.__name__}' uses dependent types, but 'dependent=True' was not specified in @typed()"
                )
            # If dependent=True, still check dependent signature
            _dependent_signature(res_func)

        # --- 1. Check parameter default values ---
        if defaults or full:
            _check_defaults_match_hints(res_func)

        # --- 2. Local-typed runtime checks
        if locals or full:
            res_func = _instrument_locals_check(res_func, force_all_annotated=full)

        # --- 3. Wrap in core typed logic
        try:
            from typed.mods.types.base import Bool
            from typed.mods.types.func import Typed, Condition
            if isinstance(res_func, Typed):
                res_func = res_func
            else:
                typed_arg = Typed(res_func)
                cod = typed_arg.cod
                if cod is Bool:
                    typed_arg.__class__ = Condition
                else:
                    typed_arg.__class__ = Typed
                res_func = typed_arg
        except Exception as e:
            raise TypedErr(f"Error in the typed function '{_name(func)}':\n {e}")

        if cache or full:
            res_func = lru_cache(maxsize=None)(res_func)

        return res_func

    if arg is not None and (isinstance(arg, TYPE) or isinstance(arg, Function)):
        if callable(arg):
            return typed_decorator(arg)
        else:
            return _variable_checker(arg)

    elif arg is not None and callable(arg):
        # User wrote @typed(function)
        return typed_decorator(arg)

    elif arg is None:
        # User wrote @typed(defaults=..., ...) or just @typed
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
        from typed.mods.types.func import Factory, Typed
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
