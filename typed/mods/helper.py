import inspect
from typing import get_type_hints, Callable, Any, Tuple, Type 

def __flat(*types):
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
            raise TypeError(f"Unsupported type in __flat: {type(item)}")
    for typ in types:
       _flatten(typ)
    if not all(isinstance(t, type) for t in flat_list):
        raise TypeError("All arguments must be types.")
    return (tuple(flat_list), is_flexible)

def __runtime_domain(func):
    def wrapper(*args, **kwargs):
        types_at_runtime = tuple(type(arg) for arg in args)
        return tuple(*types_at_runtime)
    return wrapper

def __runtime_codomain(func):
    signature = inspect.signature(func)
    return_annotation = signature.return_annotation
    if return_annotation is not inspect.Signature.empty:
        return return_annotation
    return type(None)

def __is_domain_hinted(func):
    type_hints = get_type_hints(func)
    param_hints = {param: type_hints.get(param) for param in inspect.signature(func).parameters}
    non_hinted_params = [param for param, hint in param_hints.items() if hint is None]
    if non_hinted_params:
        raise TypeError(
            f"Function '{func.__name__}' must have type hints for all parameters."
            f"\n\t --> Missing hints: '{', '.join(non_hinted_params)}'."
        )
    return True

def __is_codomain_hinted(func):
    """Check if the function has a type hint for its return value and report if missing."""
    type_hints = get_type_hints(func)
    if 'return' not in type_hints or type_hints['return'] is None:
        raise TypeError(f"Function '{func.__name__}' must have a return type hint.")
    return True

def __hinted_domain(func: Callable) -> Tuple[Type, ...]:
    type_hints = get_type_hints(func)
    if hasattr(func, '_composed_domain_hint'):
        return func._composed_domain_hint

    actual_func = func.func if hasattr(func, 'func') else func
    try:
        sig = inspect.signature(actual_func)
        return tuple(type_hints[param.name] for param in sig.parameters.values() if param.name in type_hints and type_hints[param.name] is not inspect.Signature.empty)
    except ValueError: # Handle objects without standard signatures
        pass
    return ()

def __hinted_codomain(func: Callable) -> Any:
    type_hints = get_type_hints(func)
    if hasattr(func, '_composed_codomain_hint'):
        return func._composed_codomain_hint

    actual_func = func.func if hasattr(func, 'func') else func
    try:
        sig = inspect.signature(actual_func)
        return type_hints.get('return', inspect.Signature.empty)
    except ValueError:
        pass
    return inspect.Signature.empty

def __check_domain(func, param_names, expected_domain, actual_domain, args, allow_subclass=True):
    mismatches = []
    for name, expected, actual in zip(param_names, expected_domain, actual_domain):
        expected_name = getattr(expected, '__name__', repr(expected))
        actual_name = getattr(actual, '__name__', repr(actual))
        if expected != actual:
            matched = False
            if allow_subclass and issubclass(expected, actual) and hasattr(expected, 'check'):
                matched = True
                actual_value = args[param_names.index(name)]
                if not expected.check(actual_value):
                    raise TypeError(
                        f"Domain check failed in func '{func.__name__}':"
                        f"\n\t --> '{name}': expected type '{expected_name}' did not match "
                        f"the actual value '{actual_value}'."
                    )
            if not matched:
                mismatches.append(f"\n\t --> '{name}': should be '{expected_name}', but got '{actual_name}'")
    if mismatches:
        mismatch_str = "".join(mismatches) + "."
        raise TypeError(f"Domain mismatch in func '{func.__name__}': {mismatch_str}")

def __check_codomain(func, expected_codomain, actual_codomain, result, allow_subclass=True):
    get_name = lambda x: getattr(x, '__name__', repr(x))
    if isinstance(expected_codomain, type) and isinstance(actual_codomain, type):
        if expected_codomain != actual_codomain:
            matched = False
            if allow_subclass and issubclass(actual_codomain, expected_codomain):
                matched = True
                if hasattr(expected_codomain, 'check') and not expected_codomain.check(result):
                    raise TypeError(
                        f"Codomain check failed in func '{func.__name__}': expected type operation "
                        f"'{get_name(expected_codomain)}' did not match the actual result '{result}' of type '{type(result).__name__}'."
                    )
            if not matched:
                raise TypeError(
                    f"Codomain mismatch in func '{func.__name__}': expected '{get_name(expected_codomain)}', "
                    f"but got '{get_name(actual_codomain)}'."
                )
    elif isinstance(expected_codomain, list) and isinstance(actual_codomain, type):
        if not any(
                ((issubclass(actual_codomain, ec) or (hasattr(ec, 'check') and ec.check(result)))
                for ec in expected_codomain)
        ):
            raise TypeError(
                f"Codomain mismatch in func '{func.__name__}': expected one of types '{[get_name(ec) for ec in expected_codomain]}', "
                f"but got result '{result}' of type '{get_name(actual_codomain)}'."
            )
    elif isinstance(expected_codomain, list) and isinstance(actual_codomain, list):
        checks_pass = True
        if not any(issubclass(ac, ec) or (hasattr(ec, 'check') and ec.check(result)) for ac in actual_codomain for ec in expected_codomain):
            checks_pass = False
        if not checks_pass:
            raise TypeError(
                f"Codomain mismatch in func '{func.__name__}': expected types '{[get_name(ec) for ec in expected_codomain]}', "
                f"but got types '{[get_name(ac) for ac in actual_codomain]}' for result '{result}'."
            )
    else:
        if not isinstance(result, expected_codomain):
            raise TypeError(
                f"Codomain mismatch in func '{func.__name__}': expected '{get_name(expected_codomain)}', "
                f"but got result of type '{get_name(actual_codomain)}'."
            )
