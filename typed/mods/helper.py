import inspect
from typing import get_type_hints, Callable, Any, Tuple, Type
from typed.mods.types.base import Any as TypedAny

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
    type_hints = get_type_hints(func)
    param_hints = {param: type_hints.get(param) for param in inspect.signature(func).parameters}
    non_hinted_params = [param for param, hint in param_hints.items() if hint is None]
    if non_hinted_params:
        raise TypeError(
            f"Function '{func.__name__}' must have type hints for all parameters."
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
    if hasattr(func, '_composed_domain_hint'):
        return func._composed_domain_hint
    try:
        sig = inspect.signature(original_func)
        return tuple(type_hints.get(param.name, inspect.Signature.empty)
                   for param in sig.parameters.values()
                   if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                     inspect.Parameter.POSITIONAL_ONLY,
                                     inspect.Parameter.KEYWORD_ONLY)
                   and type_hints.get(param.name, inspect.Signature.empty) is not inspect.Signature.empty)
    except ValueError:
        pass
    return ()

def _hinted_codomain(func: Callable) -> Any:
    original_func = _get_original_func(func)
    type_hints = get_type_hints(original_func)

    if hasattr(func, '_composed_codomain_hint'):
        return func._composed_codomain_hint

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

        if not isinstance(actual_value, expected_type):
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

    if expected_codomain is Any or expected_codomain is TypedAny:
        return

    if hasattr(expected_codomain, '__types__') and isinstance(expected_codomain.__types__, tuple):
        union_types = expected_codomain.__types__
        if any(isinstance(result, union_type) for union_type in union_types):
            if allow_subclass or (not allow_subclass and actual_codomain in union_types):
                if hasattr(expected_codomain, 'check') and not expected_codomain.check(result):
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

    elif isinstance(expected_codomain, list) and isinstance(actual_codomain, type):
        if not any(
                ((isinstance(result, ec) or (hasattr(ec, 'check') and ec.check(result))) # Check instance here too
                for ec in expected_codomain)
        ):
            raise TypeError(
                f"Codomain mismatch in func '{func.__name__}': expected one of types '{[get_name(ec) for ec in expected_codomain]}', "
                f"but got result '{result}' of type '{get_name(actual_codomain)}'."
            )
    else:
        raise TypeError(
            f"Codomain mismatch in func '{func.__name__}': Unexpected type combination. Expected '{get_name(expected_codomain)}', "
            f"but got result '{result}' of type '{get_name(actual_codomain)}'."
        )
