import inspect
from typing import get_type_hints, Callable, Any as Any_, Tuple, Type

def _flat(*types):
    if not types:
        return (), False
    flat_list = []
    is_flexible = True
    def _flatten(item):
       if isinstance(item, type):
           flat_list.append(item)
       elif isinstance(item, (list, tuple)):
            for sub_item in item:
                _flatten(sub_item)
       else:
            raise TypeError(f"Unsupported type in _flat: {type(item)}")
    for typ in types:
       _flatten(typ)
    if not all(isinstance(t, type) for t in flat_list):
        raise TypeError("All arguments must be types.")
    return (tuple(flat_list), is_flexible)

def _runtime_domain(func):
    def wrapper(*args, **kwargs):
        types_at_runtime = tuple(type(arg) for arg in args)
        return tuple(*types_at_runtime)
    return wrapper

def _runtime_codomain(func):
    signature = inspect.signature(func)
    return_annotation = signature.return_annotation
    if return_annotation is not inspect.Signature.empty:
        return return_annotation
    return type(None)

def _is_domain_hinted(func):
    """Check if the function has type hints for all parameters if it has any parameters."""
    sig = inspect.signature(func)
    parameters = sig.parameters

    if not parameters:
        return True

    type_hints = get_type_hints(func)
    param_hints = {param_name: type_hints.get(param_name) for param_name, param in parameters.items()}
    non_hinted_params = [param_name for param_name, hint in param_hints.items() if hint is None]

    if non_hinted_params:
        raise TypeError(
            f"Function '{func.__name__}' must have type hints for all parameters if it has any."
            f"\n\t --> Missing hints: '{', '.join(non_hinted_params)}'."
        )
    return True

def _is_codomain_hinted(func):
    """Check if the function has a type hint for its return value and report if missing."""
    type_hints = get_type_hints(func)
    if 'return' not in type_hints or type_hints['return'] is None:
        raise TypeError(f"Function '{func.__name__}' must have a return type hint.")
    return True

def _get_original_func(func: Callable) -> Callable:
    """Recursively gets the original function if it's wrapped."""
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    if hasattr(func, 'func'):
        return _get_original_func(func.func)
    return func

def _hinted_domain(func: Callable) -> Tuple[Type, ...]:
    original_func = _get_original_func(func)
    type_hints = get_type_hints(original_func)
    if hasattr(original_func, '_composed_domain_hint'):
        return original_func._composed_domain_hint
    try:
        sig = inspect.signature(original_func)
        domain_types = []
        for param in sig.parameters.values():
            if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                     inspect.Parameter.POSITIONAL_ONLY,
                                     inspect.Parameter.KEYWORD_ONLY):
                hint = type_hints.get(param.name, inspect.Signature.empty)
                if hint is not inspect.Signature.empty:
                    domain_types.append(hint)
        return tuple(domain_types)
    except ValueError:
        pass
    return ()


def _hinted_codomain(func: Callable) -> Any_:
    original_func = _get_original_func(func)
    type_hints = get_type_hints(original_func)

    if hasattr(original_func, '_composed_codomain_hint'):
        return original_func._composed_codomain_hint

    try:
        sig = inspect.signature(original_func)
        return type_hints.get('return', inspect.Signature.empty)
    except ValueError:
        pass
    return inspect.Signature.empty

def _check_domain(func, param_names, expected_domain, actual_domain, args, allow_subclass=True):
    mismatches = []
    for name, expected_type in zip(param_names, expected_domain):
        actual_value = args[param_names.index(name)]
        actual_type = type(actual_value)

        expected_name = getattr(expected_type, '__name__', repr(expected_type))
        actual_name = getattr(actual_type, '__name__', repr(actual_type))

        if isinstance(expected_type, type) and hasattr(expected_type, '__types__') and isinstance(expected_type.__types__, tuple):
            if not any(isinstance(actual_value, t) for t in expected_type.__types__):
                mismatches.append(f"\n\t --> '{name}': should be instance of one of '{[getattr(t, '__name__', str(t)) for t in expected_type.__types__]}', but got instance of '{actual_name}'")
            else:
                for t in expected_type.__types__:
                    if isinstance(actual_value, t) and hasattr(t, 'check') and not t.check(actual_value):
                        mismatches.append(f"\n\t --> '{name}': instance of '{actual_name}' failed additional check for type '{getattr(t, '__name__', str(t))}'.")
        elif not isinstance(actual_value, expected_type):
            mismatches.append(f"\n\t --> '{name}': should be instance of '{expected_name}', but got instance of '{actual_name}'")
        else:
            if hasattr(expected_type, 'check'):
                if not expected_type.check(actual_value):
                    mismatches.append(f"\n\t --> '{name}': instance of '{actual_name}' failed additional check for type '{expected_name}'.")

    if mismatches:
        mismatch_str = "".join(mismatches) + "."
        raise TypeError(f"Domain mismatch in func '{func.__name__}': {mismatch_str}")


def _check_codomain(func, expected_codomain, actual_codomain, result, allow_subclass=True):
    get_name = lambda x: getattr(x, '__name__', repr(x))

    from typed.mods.types.base import Any_ as TypedAny_
    if expected_codomain is Any_ or expected_codomain is TypedAny_ or expected_codomain is inspect.Signature.empty:
        return

    if isinstance(expected_codomain, type) and hasattr(expected_codomain, '__types__') and isinstance(expected_codomain.__types__, tuple):
        union_types = expected_codomain.__types__
        if any(isinstance(result, union_type) for union_type in union_types):
            for t in union_types:
                if isinstance(result, t) and hasattr(t, 'check') and not t.check(result):
                    raise TypeError(
                        f"Codomain check failed in func '{func.__name__}': expected Union with checks did not match "
                        f"the actual result '{result}' of type '{get_name(actual_codomain)}'."
                    )
            return

        expected_union_names = [get_name(t) for t in union_types]
        raise TypeError(
            f"Codomain mismatch in func '{func.__name__}': expected one of types '{expected_union_names}', "
            f"but got result '{result}' of type '{get_name(actual_codomain)}'."
        )

    elif isinstance(expected_codomain, type):
        if isinstance(result, expected_codomain):
            if allow_subclass or (not allow_subclass and actual_codomain is expected_codomain):
                if hasattr(expected_codomain, 'check') and not expected_codomain.check(result):
                    raise TypeError(
                        f"Codomain check failed in func '{func.__name__}': expected type operation "
                        f"'{get_name(expected_codomain)}' did not match the actual result '{result}' of type '{type(result).__name__}'."
                    )
                return

        raise TypeError(
            f"Codomain mismatch in func '{func.__name__}': expected '{get_name(expected_codomain)}' "
            f"(allow_subclass={allow_subclass}), but got result '{result}' of type '{get_name(actual_codomain)}'."
        )
    else:
        if not isinstance(result, expected_codomain):
            raise TypeError(
                f"Codomain mismatch in func '{func.__name__}': Expected '{get_name(expected_codomain)}' "
                f"but got result '{result}' of type '{get_name(actual_codomain)}'."
            )

