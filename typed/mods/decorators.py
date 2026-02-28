from typed.mods.types.base import TYPE
from typed.mods.types.func import Function
from functools import lru_cache, update_wrapper
from typed.mods.helper.general import _name
from typed.mods.helper.func import (
    _has_dependent_type,
    _dependent_signature,
    _check_defaults_match_hints,
    _instrument_locals_check,
)

def function(*args, **kwargs):
    if args and callable(args[0]) and len(args) == 1 and not kwargs:
        f = args[0]
        return Function(f)

    def decorator(f):
        return Function(f, **kwargs)

    return decorator

def partial(func):
    def wrapper(*args, **kwargs):
        from typed.mods.helper.general import _
        underscore_to_check = _
        has_underscore = (
            (underscore_to_check in args)
            or any(v is underscore_to_check for v in kwargs.values())
        )
        if has_underscore:
            from typed.mods.types.func import Partial
            partial_instance = object.__new__(Partial)
            partial_instance.__init__(func, args, kwargs)
            return partial_instance
        else:
            return func(*args, **kwargs)

    update_wrapper(wrapper, func)

    underlying = getattr(func, "func", func)
    wrapper.func = underlying

    for attr in ("domain", "dom", "codomain", "cod"):
        if hasattr(func, attr):
            setattr(wrapper, attr, getattr(func, attr))

    return wrapper

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

def typed(
    arg=None,
    *,
    defaults=False,
    cache=False,
    locals=False,
    rigid=False,
    dependent=False,
    lazy=True,
    enclose=None,
    message=None,
    partials=True,
):
    def _build_typed(res_func):
        from typed.mods.types.func import Lazy

        if isinstance(res_func, Lazy):
            res_func = res_func.func

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
            res_func = _instrument_locals_check(
                res_func, force_all_annotated=rigid
            )

        base_func = res_func
        if cache:
            base_func = lru_cache(maxsize=None)(base_func)

        try:
            from typed.mods.types.base import Bool
            from typed.mods.types.func import Typed, Condition

            if isinstance(base_func, Typed):
                typed_func = base_func
            else:
                typed_func = Typed(base_func)

            cod = typed_func.cod
            if cod is Bool:
                typed_func.__class__ = Condition
            else:
                typed_func.__class__ = Typed

            res_func = typed_func
        except Exception as e:
            raise TypedErr(
                f"Error in the typed function '{_name(res_func)}':\n {e}"
            )

        if enclose is not None:
            orig = res_func

            def _enclosed(*a, **kw):
                try:
                    return orig(*a, **kw)
                except Exception as e:
                    msg = message.format(e=e) if message is not None else str(e)
                    raise enclose(msg) from e

            update_wrapper(_enclosed, orig)
            _enclosed.func = getattr(orig, "func", orig)
            res_func = _enclosed

        return res_func

    def _make_lazy_wrapper(func):
        from typed.mods.types.func import Lazy
        return Lazy(func)

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
                self.func = original
                self.__wrapped__ = original

            def __call__(self, *a, **kw):
                return self.func(*a, **kw)

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

