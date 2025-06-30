import re
import inspect
from typing import get_type_hints

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
            f"'{func.__name__}':  missing type hints for the following parameters:\n"
            f"  ==> '{', '.join(non_hinted_params)}'."
        )
    return True

def _is_codomain_hinted(func):
    """Check if the function has a type hint for its return value and report if missing."""
    type_hints = get_type_hints(func)
    if 'return' not in type_hints or type_hints['return'] is None:
        raise TypeError(f"Function '{func.__name__}' must have a return type hint.")
    return True

def _get_original_func(func):
    """Recursively gets the original function if it's wrapped."""
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    if hasattr(func, 'func'):
        return _get_original_func(func.func)
    return func

def _hinted_domain(func):
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

def _hinted_codomain(func):
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

def _get_type_display_name(tp):
    if hasattr(tp, '__display__'):
        return tp.__display__
    if hasattr(tp, '__types__'):
        types = tp.__types__
        cname = getattr(tp, '__name__', '')
        if tuple in getattr(tp, '__bases__', ()):
            return f"Prod({', '.join(_get_type_display_name(t) for t in types)})"
        elif 'union' in cname.lower():
            return f"Union({', '.join(_get_type_display_name(t) for t in types)})"
        else:
            return ', '.join(_get_type_display_name(t) for t in types)
    name = getattr(tp, '__name__', None)
    if name in ['int', 'float', 'str', 'bool']:
        return name.capitalize()
    if name == 'NoneType':
        return "Nill"
    return name or str(tp)

def _check_domain(func, param_names, expected_domain, actual_domain, args, allow_subclass=True):
    mismatches = []
    for i, (name, expected_type) in enumerate(zip(param_names, expected_domain)):
        actual_value = args[i]
        actual_type = type(actual_value)

        expected_display_name = _get_type_display_name(expected_type)
        actual_display_name = _get_type_display_name(actual_type)

        if not isinstance(actual_value, expected_type):
            mismatches.append(f"\n ==> '{name}' has value '{actual_value}'")
            mismatches.append(f"\n     [expected_type]: '{expected_display_name}'")
            mismatches.append(f"\n     [received_type]: '{actual_display_name}'")
        elif hasattr(expected_type, 'check'):
            if not expected_type.check(actual_value):
                mismatches.append(f"\n ==> '{name}' has value '{actual_value}'")
                mismatches.append(f"\n     [expected_type]: '{expected_display_name}'")
                mismatches.append(f"\n     [received_type]: '{actual_display_name}'")

    if mismatches:
        mismatch_str = "".join(mismatches) + "."
        raise TypeError(f"Domain mismatch in func '{func.__name__}': {mismatch_str}")

def _check_codomain(func, expected_codomain, actual_codomain, result, allow_subclass=True):
    expected_display_name = _get_type_display_name(expected_codomain)
    actual_display_name = _get_type_display_name(actual_codomain)

    if (
        isinstance(expected_codomain, type)
        and hasattr(expected_codomain, '__types__')
        and isinstance(expected_codomain.__types__, tuple)
        and expected_codomain.__name__.startswith('Union')
    ):
        union_types = expected_codomain.__types__
        if any(isinstance(result, union_type) for union_type in union_types):
            for t in union_types:
                if isinstance(result, t):
                    if hasattr(t, 'check') and not t.check(result):
                        raise TypeError(
                            f"Codomain mismatch in func '{func.__name__}':"
                            f"\n ==> received the value '{result}'."
                            f"\n     [expected_type]: '{expected_display_name}'"
                            f"\n     [received_type]: '{actual_display_name}'"
                            f"\n     [failed_typed]:  '{_get_type_display_name(t)}'"
                        )
            return

        expected_union_names = [_get_type_display_name(t) for t in union_types]
        raise TypeError(
            f"Codomain mismatch in func '{func.__name__}':"
            f"\n ==> received the value '{result}'."
            f"\n     [expected_type]: 'Union({', '.join(expected_union_names)})'."
            f"\n     [received_type]: '{actual_display_name}'"
        )

    if not isinstance(result, expected_codomain):
        raise TypeError(
            f"Codomain mismatch in func '{func.__name__}':"
            f"\n ==> received the value '{result}'."
            f"\n     [expected_type]: '{expected_display_name}'"
            f"\n     [received_type]: '{actual_display_name}'"
        )
    elif hasattr(expected_codomain, 'check') and not expected_codomain.check(result):
        raise TypeError(
            f"Codomain mismatch in func '{func.__name__}':"
            f"\n ==> received the value '{result}'."
            f"\n    [expected_type]: '{expected_display_name}'"
            f"\n    [received_type]: '{actual_display_name}'"
            f"\n    [failed_typed]:  '{_get_type_display_name(expected_codomain)}'"
        )

class _Any(type):
    def __instancecheck__(cls, instance):
        return True
    def __subclasscheck__(cls, subclass):
        return True

class _Pattern(type):
    def __instancecheck__(cls, x):
        if not isinstance(x, str):
            return False
        try:
            re.compile(x)
            return True
        except re.error:
            return False
    def __subclasscheck__(cls, sub):
        return issubclass(sub, str)
    def __repr__(cls):
        return "Pattern(str): a string valid as Python regex"

def _nill() -> type(None):
        pass

def _builtin_nulls():
    from typed.mods.factories.base import List, Tuple, Set, Dict
    from typed.mods.types.func import TypedFuncType
    from typed.models import Model, MODEL, Exact, EXACT

    Pattern = _Pattern("Pattern", (str,), {})

    return {
        Dict: {},
        dict: {},
        Tuple: (),
        tuple: (),
        List: [],
        list: [],
        Set: set(),
        set: set(),
        frozenset: frozenset(),
        str: "",
        int: 0,
        float: 0.0,
        bool: False,
        type(None): None,
        TypedFuncType: TypedFuncType(_nill),
        Pattern: r'',
        MODEL: Model(),
        EXACT: Exact()
    }

def _get_null_object(typ):
    from typed.models import MODEL, EXACT, CONDITIONAL
    if any(isinstance(typ, kind) for kind in (MODEL, EXACT, CONDITIONAL)):
        required = dict(getattr(typ, '_required_attributes_and_types', ()))
        optional = getattr(typ, '_optional_attributes_and_defaults', {})
        result = {}
        for key, field_type in required.items():
            result[key] = _get_null_object(field_type)
        for key, wrapper in optional.items():
            if hasattr(wrapper, "default_value"):
                result[key] = wrapper.default_value
            else:
                result[key] = _get_null_object(wrapper.type)
        return result

    if typ in _builtin_nulls():
        return _builtin_nulls()[typ]
    if hasattr(typ, '__bases__'):
        bases = typ.__bases__
        if list in bases:
            if hasattr(typ, '__types__') and typ.__types__:
                elem_null = _get_null_object(typ.__types__[0])
                return [elem_null]
            else:
                return []
        if tuple in bases:
            if hasattr(typ, '__types__') and typ.__types__:
                if hasattr(typ, '__name__') and typ.__name__.startswith("Prod"):
                    return tuple(_get_null_object(t) for t in typ.__types__)
                return tuple()
            else:
                return ()
        if set in bases:
            if hasattr(typ, '__types__') and typ.__types__:
                elem_null = _get_null_object(typ.__types__[0])
                return {elem_null}
            else:
                return set()
        if dict in bases:
            if hasattr(typ, '__types__') and typ.__types__:
                vtyp = typ.__types__[0]
                vnull = _get_null_object(vtyp)
                if vtyp in (str,):
                    return {"": vnull}
                elif vtyp in (int,):
                    return {0: vnull}
                elif vtyp in (float,):
                    return {0.0: vnull}
                else:
                    return {None: vnull}
            else:
                return {}
    return None

def _is_null_of_type(x, typ):
    null = _get_null_object(typ)
    if typ in _builtin_nulls().keys():
        return x == _builtin_nulls()[typ]
    if hasattr(typ, '__bases__'):
        base = typ.__bases__[0]
        return x == null and isinstance(x, base)
    return x == null

def _variable_checker(typ):
    def wrapper(x):
        if not isinstance(x, typ):
            raise TypeError(
                f"Mismatch type in variable value.\n"
                f" ==> received value '{x}':\n"
                f"     [expected_type]: '{_get_type_display_name(typ)}'\n"
                f"     [received_type]: '{_get_type_display_name(type(x))}'"
            )
        return x
    return wrapper
