from inspect import signature, Parameter, Signature, isclass
from typing import get_type_hints
from typed.mods.helper.general import _type, _name, _issubtype

def _unwrap(func):
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    if hasattr(func, 'func'):
        return _unwrap(func.func)
    return func

def _get_args(self):
    func = getattr(self, 'func', self)
    sig = signature(func)
    hints = get_type_hints(func)
    result = {}
    for name, param in sig.parameters.items():
        if param.kind in (
            Parameter.POSITIONAL_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
            Parameter.KEYWORD_ONLY,
        ):
            ann = hints.get(name, None)
            result[name] = {
                "type": ann,
                "default": param.default
            }
    return result

def _get_kwargs(self):
    all_args = _get_args(self)
    from typed.mods.types.base import Nill
    return {
        name: info
        for name, info in all_args.items()
        if info['default'] is not Nill
    }

def _get_pos_args(self):
    all_args = _get_args(self)
    from typed.mods.types.base import Nill
    return {
        name: info
        for name, info in all_args.items()
        if info['default'] is Nill
    }
def _get_num_args(func):
    """
    1. Returns the number of fixed arguments of a function.
    2. Returns -1 if the function contains *args or **kwargs.
    """
    signature = signature(func)
    num_args = 0
    for param in signature.parameters.values():
        if param.kind == param.VAR_POSITIONAL or param.kind == param.VAR_KEYWORD:
            return -1
        else:
            num_args += 1
    return num_args

def _get_num_kwargs(func):
    """
    1. Returns the number of keyword arguments of a function.
    2. Returns -1 if the function contains *args or **kwargs.
    """
    sig = signature(func)
    count = 0
    for param in sig.parameters.values():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        if param.default is not param.empty:
            count += 1
    return count

def _get_num_posargs(func):
    """
    Returns the number of required positional arguments (no default).
    Returns -1 if the function contains *args or **kwargs.
    """
    signature = signature(func)
    num_args = 0
    for param in signature.parameters.values():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            return -1
        if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD) and param.default is param.empty:
            num_args += 1
    return num_args

def _is_composable(*funcs, revert: bool = False) -> bool:
    if len(funcs) < 2:
        return False

    seq = list(funcs)
    if revert:
        seq = list(reversed(seq))

    for f, g in zip(seq, seq[1:]):
        cod = getattr(f, "cod", getattr(f, "codomain", None))
        dom = getattr(g, "dom", getattr(g, "domain", None))
        if cod is None or dom is None:
            return False

        try:
            dom_tuple = tuple(dom)
        except TypeError:
            dom_tuple = (dom,)

        if not dom_tuple:
            return False

        dom0 = dom_tuple[0]

        if not (cod <= dom0):
            return False

    return True

def _runtime_domain(func):
    def wrapper(*args, **kwargs):
        from typed.mods.types.base import TYPE
        types_at_runtime = tuple(TYPE(arg) for arg in args)
        return tuple(*types_at_runtime)
    return wrapper

def _runtime_codomain(func):
    signature = signature(func)
    return_annotation = signature.return_annotation
    if return_annotation is not Signature.empty:
        return return_annotation
    from typed.mods.types.base import Nill
    return Nill

def _is_domain_hinted(func):
    """Check if the function has type hints for all parameters if it has any parameters."""
    sig = signature(func)
    parameters = sig.parameters

    if not parameters:
        return True

    type_hints = get_type_hints(func)
    param_hints = {param_name: type_hints.get(param_name) for param_name, param in parameters.items()}
    non_hinted_params = [param_name for param_name, hint in param_hints.items() if hint is None]

    if non_hinted_params:
        raise TypeError(
             "Type hints are missing.\n"
            f"'{func.__name__}':  missing type hints for the following parameters:\n"
            f"  ==> '{', '.join(non_hinted_params)}'."
        )
    return True

def _is_codomain_hinted(func):
    """Check if the function has a type hint for its return value and report if missing."""
    type_hints = get_type_hints(func)
    if 'return' not in type_hints or type_hints['return'] is None:
        raise TypeError(
            "Type hints are missing.\n"
            f" ==> {_name(func)}: missing return type hint."
        )
    return True

def _hinted_domain(func):
    original_func = _unwrap(func)
    type_hints = get_type_hints(original_func)
    if hasattr(original_func, '_composed_domain_hint'):
        return original_func._composed_domain_hint
    try:
        sig = signature(original_func)
        domain_types = []
        for param in sig.parameters.values():
            if param.kind in (Parameter.POSITIONAL_OR_KEYWORD,
                                     Parameter.POSITIONAL_ONLY,
                                     Parameter.KEYWORD_ONLY):
                hint = type_hints.get(param.name, Signature.empty)
                if hint is not Signature.empty:
                    domain_types.append(hint)
        return tuple(domain_types)
    except ValueError:
        pass
    return ()

def _hinted_codomain(func):
    original_func = _unwrap(func)
    type_hints = get_type_hints(original_func)

    if hasattr(original_func, '_composed_codomain_hint'):
        return original_func._composed_codomain_hint

    try:
        sig = signature(original_func)
        return type_hints.get('return', Signature.empty)
    except ValueError:
        pass
    return Signature.empty

def _check_domain(func, param_names, expected_domain, actual_domain, args, allow_subclass=True):
    mismatches = []
    param_value_map = dict(zip(param_names, args))

    from typed.mods.types.base import TYPE
    for i, (name, expected_type) in enumerate(zip(param_names, expected_domain)):
        actual_value = args[i]
        actual_type = TYPE(actual_value)
        actual_display_name = _name(actual_type)

        if callable(expected_type) and not isinstance(expected_type, TYPE) and not isclass(expected_type):
            original = getattr(expected_type, "_dependent_func", expected_type)
            expected_sig = signature(original)
            dep_args = [
                param_value_map[pname]
                for pname in expected_sig.parameters
                if pname in param_value_map
            ]
            expected_type_resolved = original(*dep_args)
        else:
            expected_type_resolved = expected_type

        if not isinstance(actual_value, expected_type_resolved) and not _issubtype(TYPE(actual_value), expected_type_resolved):
            if getattr(TYPE(actual_value), 'is_model', False) and getattr(expected_type_resolved, 'is_model', False):
                if not _issubtype(TYPE(actual_value), expected_type_resolved):
                    mismatches.append(f" ==> '{name}': has value '{_name(actual_value)}'\n")
                    mismatches.append(f"     [expected_type] '{_name(expected_type_resolved)}'\n")
                    mismatches.append(f"     [received_type] '{actual_display_name}'\n")
                else:
                    return True
            else:
                mismatches.append(f" ==> '{name}': has value '{_name(actual_value)}'\n")
                mismatches.append(f"     [expected_type] '{_name(expected_type_resolved)}'\n")
                mismatches.append(f"     [received_type] '{actual_display_name}'\n")
        elif hasattr(expected_type_resolved, 'check'):
            if not expected_type_resolved.check(actual_value):
                mismatches.append(f" ==> '{name}': has value '{_name(actual_value)}'\n")
                mismatches.append(f"     [expected_type] '{_name(expected_type_resolved)}'\n")
                mismatches.append(f"     [received_type] '{actual_display_name}'")

    if mismatches:
        mismatch_str = "".join(mismatches)
        raise TypeError(f"Domain mismatch in func '{func.__name__}':\n {mismatch_str}")

    return True

def _check_codomain(func, expected_codomain, actual_codomain, result, allow_subclass=True, param_value_map=None):
    expected_display_name = _name(expected_codomain)
    actual_display_name = _name(actual_codomain)

    from typed.mods.types.base import TYPE
    if callable(expected_codomain) and not isinstance(expected_codomain, TYPE) and not isclass(expected_codomain):
        import inspect
        expected_sig = inspect.signature(expected_codomain)
        if param_value_map is None:
            raise TypeError(f"param_value_map required for dependent codomain '{func.__name__}'")
        dep_args = [
            param_value_map[pname]
            for pname in expected_sig.parameters
            if pname in param_value_map
        ]
        expected_codomain_resolved = expected_codomain(*dep_args)
    else:
        expected_codomain_resolved = expected_codomain

    if (
        isinstance(expected_codomain_resolved, TYPE)
        and hasattr(expected_codomain_resolved, '__types__')
        and isinstance(expected_codomain_resolved.__types__, tuple)
        and expected_codomain_resolved.__name__.startswith('Union')
    ):
        union_types = expected_codomain_resolved.__types__
        if any(isinstance(result, union_type) for union_type in union_types):
            for t in union_types:
                if isinstance(result, t):
                    if hasattr(t, 'check') and not t.check(result):
                        raise TypeError(
                            f"Codomain mismatch in func '{_name(func)}':\n"
                            f" ==> received the value '{result}'.\n"
                            f"     [expected_type] '{expected_display_name}'\n"
                            f"     [received_type] '{actual_display_name}'\n"
                            f"     [failed_typed]  '{_name(t)}'"
                        )
            return
        expected_union_names = [_name(t) for t in union_types]
        raise TypeError(
            f"Codomain mismatch in func '{_name(func)}':\n"
            f" ==> received the value '{result}'.\n"
            f"     [expected_type]: 'Union({', '.join(expected_union_names)})'.\n"
            f"     [received_type]: '{actual_display_name}'"
        )

    if not isinstance(result, expected_codomain_resolved):
        raise TypeError(
            f"Codomain mismatch in func '{_name(func)}':\n"
            f" ==> received the value '{result}'.\n"
            f"     [expected_type]: '{_name(expected_codomain_resolved)}'\n"
            f"     [received_type]: '{actual_display_name}'"
        )
    elif hasattr(expected_codomain_resolved, 'check') and not expected_codomain_resolved.check(result):
        raise TypeError(
            f"Codomain mismatch in func '{_name(func)}':\n"
            f" ==> received the value '{result}'.\n"
            f"    [expected_type]: '{_name(expected_codomain_resolved)}'\n"
            f"    [received_type]: '{actual_display_name}'\n"
            f"    [failed_typed]:  '{_name(expected_codomain_resolved)}'"
        )
    return True


def _has_dependent_type(func):
    sig = signature(func)
    anns = get_type_hints(func)
    for name, param in sig.parameters.items():
        typ = anns.get(name, None)
        if hasattr(typ, 'is_dependent_type') and getattr(typ, 'is_dependent_type'):
            return True
    return False

def _check_dependent_signature(dep_type, using_func):
    """
    Checks that, for each argument of using_func annotated with dep_type,
    every parameter expected by dep_type exists in using_func with matching type annotation.
    """
    dep_func   = _unwrap(dep_type)
    using_func = _unwrap(using_func)

    dep_sig    = signature(dep_func)
    dep_anns   = dep_func.__annotations__
    using_sig  = signature(using_func)
    using_anns = using_func.__annotations__

    for uname, param in using_sig.parameters.items():
        if param.annotation is dep_type:
            for dep_name in dep_sig.parameters:
                if dep_name not in using_sig.parameters:
                    raise TypeError(
                        f"{using_func.__name__}: argument '{uname}' uses dependent type '{dep_func.__name__}'"
                        f" which expects param '{dep_name}', but it is missing in this function's parameters."
                    )
                if dep_anns.get(dep_name) != using_anns.get(dep_name):
                    raise TypeError(
                        f"{using_func.__name__}: argument '{uname}' uses dependent type '{dep_func.__name__}'."
                        f"\nParameter '{dep_name}': expected type {dep_anns.get(dep_name)!r},"
                        f" got {using_anns.get(dep_name)!r}."
                    )

def _dependent_signature(func):
    sig = signature(func)
    for name, param in sig.parameters.items():
        ann = param.annotation
        if hasattr(ann, 'is_dependent_type'):
            _check_dependent_signature(ann, func)
    return func

def _check_defaults_match_hints(func):
    """Ensure all default values of parameters match their type hints."""
    sig = signature(func)
    hints = get_type_hints(func)
    mismatches = []
    for name, param in sig.parameters.items():
        if param.default is not Parameter.empty:
            hint = hints.get(name)
            default = param.default
            if hint is not None and not isinstance(default, hint):
                mismatches.append(
                    f" ==> '{func.__name__}': parameter '{name}' default value {default!r} does not match hint '{hint.__name__}'."
                )
    if mismatches:
        raise TypeError(
            "Default values do not match annotations:\n" +
            "\n".join(mismatches)
        )

def _instrument_locals_check(func, force_all_annotated=True):
    """
    Wrap the function so that local variable type checks are inserted.
    The actual instrumentation is deferred until the first call.
    """
    from inspect import getsourcelines
    from textwrap import dedent
    from ast import parse, walk, AnnAssign, Name, Assign, unparse, FunctionDef
    from functools import wraps, update_wrapper
    import re

    try:
        lines, _ = getsourcelines(func)
    except OSError:
        return func

    src = dedent(''.join(lines))
    tree = parse(src, type_comments=True)
    fn_node = next((n for n in tree.body if isinstance(n, FunctionDef)), None)
    if fn_node is None:
        return func

    annotated_locs = []
    all_locs = set()
    for node in walk(fn_node):
        if isinstance(node, AnnAssign) and isinstance(node.target, Name):
            annotated_locs.append((node.target.id, node.annotation))
            all_locs.add(node.target.id)
        elif isinstance(node, Assign):
            for target in node.targets:
                if isinstance(target, Name):
                    all_locs.add(target.id)

    if force_all_annotated:
        not_annot = set(all_locs) - {name for name, _ in annotated_locs}
        if not_annot:
            raise TypeError(
                f"Missing type hints in local variables:"
                f"  ==> '{func.__name__}': local var '{not_annot}' was not typed."
            )

    if not annotated_locs:
        return func

    name_to_type = {name: unparse(typ) for name, typ in annotated_locs}

    original_globals = func.__globals__.copy()
    original_globals['_type'] = _type

    instrumented = None

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal instrumented
        if instrumented is None:
            instrumented_lines = []

            for line in lines:
                clean_line = line.rstrip('\n')
                instrumented_lines.append(clean_line)

                for name, type_str in name_to_type.items():
                    if re.match(rf'^\s*{re.escape(name)}\s*=.*', clean_line):
                        check = f"""
                            if not isinstance({name}, {type_str}):
                                raise TypeError(
                                    "Wrong type in function '{func.__name__}'\\n"
                                    "  ==> '{func.__name__}': local var '{name}' has an unexpected type\\n"
                                    "      [expected_type] {type_str}\\n"
                                    f"      [received_type] {{_type({name}).__name__}}")
                        """
                        for check_line in check.splitlines():
                            instrumented_lines.append(check_line)

            return_indices = [i for i, l in enumerate(instrumented_lines)
                              if l.strip().startswith('return')]
            for idx in reversed(return_indices):
                for name, type_str in name_to_type.items():
                    check = f"""
                if not isinstance({name}, {type_str}):
                    raise TypeError(
                        "Wrong type in function '{func.__name__}'\\n"
                        "  ==> '{func.__name__}': local var '{name}' has an unexpected type\\n"
                        "      [expected_type] {type_str}\\n"
                        f"      [received_type] {{_type({name}).__name__}}")
            """
                    for check_line in reversed(check.splitlines()):
                        instrumented_lines.insert(idx, check_line)

            code_joined = "\n".join(instrumented_lines)
            locs = {}
            exec(code_joined, original_globals, locs)
            instrumented = locs[func.__name__]
            instrumented.__wrapped__ = func
            update_wrapper(instrumented, func)

        return instrumented(*args, **kwargs)

    wrapper.__wrapped__ = func
    return wrapper

def _variable_checker(typ):
    def wrapper(x):
        if not isinstance(x, typ):
            from typed.mods.types.base import TYPE
            raise TypeError(
                f"Mismatch type in variable value.\n"
                f" ==> received value '{x}':\n"
                f"     [expected_type]: '{_name(typ)}'\n"
                f"     [received_type]: '{_name(TYPE(x))}'"
            )
        return x
    return wrapper
