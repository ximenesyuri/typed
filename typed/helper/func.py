from functools import lru_cache
from typed.mods.err import Err, TypeErr, HintErr, DomErr, CodErr

@lru_cache(maxsize=512)
def signature(func):
    from inspect import signature as _signature
    return _signature(func)

@lru_cache(maxsize=512)
def hints(func):
    from typing import get_type_hints
    return get_type_hints(func)

def _unwrap(obj):
    seen = set()
    while True:
        obj_id = id(obj)
        if obj_id in seen:
            break
        seen.add(obj_id)

        if hasattr(obj, "__wrapped__"): obj = obj.__wrapped__
        elif hasattr(obj, "original_func"): obj = obj.original_func
        elif hasattr(obj, "func") and callable(getattr(obj, "func")): obj = obj.func
        elif hasattr(obj, "_orig"): obj = obj._orig
        else: break
    return obj

def _get_args(self):
    func = getattr(self, 'func', self)
    sig = signature(func)
    hints_dict = hints(func)
    from inspect import Parameter

    return {
        name: {"type": hints_dict.get(name, None), "default": param.default}
        for name, param in sig.parameters.items()
        if param.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
    }

def _get_kwargs(self):
    all_args = _get_args(self)
    from typed.mods.types.base import Nill
    return {n: info for n, info in all_args.items() if info['default'] is not Nill}

def _get_pos_args(self):
    all_args = _get_args(self)
    from typed.mods.types.base import Nill
    return {n: info for n, info in all_args.items() if info['default'] is Nill}

def _is_composable(*funcs, revert: bool = False) -> bool:
    if len(funcs) < 2: return False
    seq = funcs[::-1] if revert else funcs

    for f, g in zip(seq, seq[1:]):
        cod = getattr(f, "cod", getattr(f, "codomain", None))
        dom = getattr(g, "dom", getattr(g, "domain", None))
        if cod is None or dom is None: return False

        dom_tuple = tuple(dom) if hasattr(dom, "__iter__") and not isinstance(dom, str) else (dom,)
        if not dom_tuple or not (cod <= dom_tuple[0]):
            return False

    return True

def _runtime_domain(func):
    def wrapper(*args, **kwargs):
        from typed.mods.types.base import TYPE
        return tuple(TYPE(arg) for arg in args)
    return wrapper

def _runtime_codomain(func):
    sig = signature(func)
    from inspect import Signature
    if sig.return_annotation is not Signature.empty:
        return sig.return_annotation
    from typed.mods.types.base import Nill
    return Nill

def _is_domain_hinted(func):
    sig = signature(func)
    if not sig.parameters: return True

    type_hints = hints(func)
    non_hinted_params = [p for p in sig.parameters if type_hints.get(p) is None]

    if non_hinted_params:
        raise HintErr(term=func, arg=None, message=f"Missing type hints for parameters: {', '.join(non_hinted_params)}")
    return True

def _is_codomain_hinted(func):
    type_hints = hints(func)
    if type_hints.get('return') is None:
        raise HintErr(term=func, arg=None, message="Missing return type hint")
    return True

def _hinted_domain(func):
    original_func = _unwrap(func)
    if hasattr(original_func, '_composed_domain_hint'):
        return original_func._composed_domain_hint
    type_hints = hints(original_func)
    try:
        from inspect import Parameter, Signature
        sig = signature(original_func)
        domain_types = []
        for param in sig.parameters.values():
            if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.POSITIONAL_ONLY, Parameter.KEYWORD_ONLY):
                hint = type_hints.get(param.name, Signature.empty)
                if hint is not Signature.empty:
                    domain_types.append(hint)
        return tuple(domain_types)
    except ValueError:
        return ()

def _hinted_codomain(func):
    original_func = _unwrap(func)
    if hasattr(original_func, '_composed_codomain_hint'):
        return original_func._composed_codomain_hint

    type_hints = hints(original_func)
    from inspect import Signature
    return type_hints.get('return', Signature.empty)

def _check_domain(func, paramnames, expected_domain, actual_domain, args, allow_subclass=True):
    from typed.mods.core import type, isterm

    for p_name, expected_type, actual_value in zip(paramnames, expected_domain, args):
        actual_type = type(actual_value)

        # Replaced isinstance with framework isterm
        if not isterm(actual_value, expected_type):
            raise DomErr(term=func, arg=p_name, expected=expected_type, received=actual_type)
        elif hasattr(expected_type, 'check') and not expected_type.check(actual_value):
            raise DomErr(term=func, arg=p_name, expected=expected_type, received=actual_type)

    return True

def _check_codomain(func, expected_codomain, actual_codomain, result, allow_subclass=True):
    from typed.mods.core import type, isterm
    from typed.mods.types.base import TYPE

    actual_type = type(result)

    if (isinstance(expected_codomain, TYPE) and
        hasattr(expected_codomain, '__types__') and 
        isinstance(expected_codomain.__types__, tuple) and 
        expected_codomain._name__.startswith('Union')):

        union_types = expected_codomain.__types__
        # Replaced isinstance with framework isterm
        if any(isterm(result, t) for t in union_types):
            for t in union_types:
                if isterm(result, t) and hasattr(t, 'check') and not t.check(result):
                    raise CodErr(term=func, expected=t, received=actual_type)
            return True
        raise CodErr(term=func, expected=expected_codomain, received=actual_type)

    if not isterm(result, expected_codomain):
        raise CodErr(term=func, expected=expected_codomain, received=actual_type)
    elif hasattr(expected_codomain, 'check') and not expected_codomain.check(result):
        raise CodErr(term=func, expected=expected_codomain, received=actual_type)

    return True

def _check_defaults_match_hints(func):
    from inspect import Parameter
    sig = signature(func)
    type_hints = hints(func)
    for p_name, param in sig.parameters.items():
        if param.default is not Parameter.empty:
            hint = type_hints.get(p_name)
            if hint is not None:
                from typed.mods.core import type, isterm
                if not isterm(param.default, hint):
                    raise TypeErr(term=func, arg=p_name, expected=hint, received=type(param.default), message="Default value does not match hint.")

def _instrument_locals_check(func, force_all_annotated=True):
    from functools import wraps, update_wrapper

    instrumented_func = None

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal instrumented_func

        if instrumented_func is None:
            import inspect
            import ast
            from textwrap import dedent
            from typed.mods.core import type, isterm

            try:
                lines, _ = inspect.getsourcelines(func)
            except OSError:
                instrumented_func = func
                return instrumented_func(*args, **kwargs)

            src = dedent(''.join(lines))
            tree = ast.parse(src, type_comments=True)

            fn_node = next((n for n in tree.body if isinstance(n, ast.FunctionDef)), None)
            if fn_node is None:
                instrumented_func = func
                return instrumented_func(*args, **kwargs)

            fn_node.decorator_list.clear()

            annotated_locs = {}
            all_locs = set()

            for node in ast.walk(fn_node):
                if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    annotated_locs[node.target.id] = ast.unparse(node.annotation)
                    all_locs.add(node.target.id)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            all_locs.add(target.id)

            if force_all_annotated:
                not_annot = all_locs - set(annotated_locs.keys())
                if not_annot:
                    raise HintErr(term=func, arg=None, message=f"Local var '{list(not_annot)}' was not typed.")

            if not annotated_locs:
                instrumented_func = func
                return instrumented_func(*args, **kwargs)

            class TypeCheckInjector(ast.NodeTransformer):
                def _create_check(self, var_name, type_str):
                    chk_code = f"if not isterm({var_name}, {type_str}): __raise_err('{var_name}', {var_name}, {type_str}, __func_obj)"
                    return ast.parse(chk_code).body

                def visit_Assign(self, node):
                    self.generic_visit(node)
                    nodes = [node] 
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id in annotated_locs:
                            nodes.extend(self._create_check(target.id, annotated_locs[target.id]))
                    return nodes 

                def visit_AnnAssign(self, node):
                    self.generic_visit(node)
                    nodes = [node]
                    if isinstance(node.target, ast.Name) and node.target.id in annotated_locs:
                        nodes.extend(self._create_check(node.target.id, annotated_locs[node.target.id]))
                    return nodes

            tree = TypeCheckInjector().visit(tree)
            ast.fix_missing_locations(tree)

            code_obj = compile(tree, filename=f"<instrumented {func.__name__}>", mode="exec")

            def __raise_err(var_name, val, expected, func_obj):
                raise TypeErr(
                    message=f"Local var '{var_name}' has an unexpected type", 
                    term=func_obj, 
                    arg=var_name, 
                    expected=expected, 
                    received=type(val)
                )

            original_globals = func.__globals__.copy()
            original_globals['type'] = type
            original_globals['isterm'] = isterm
            original_globals['__func_obj'] = func
            original_globals['__raise_err'] = __raise_err
            locs = {}

            exec(code_obj, original_globals, locs)

            instrumented_func = locs[func.__name__]
            instrumented_func.__wrapped__ = func
            update_wrapper(instrumented_func, func)

        return instrumented_func(*args, **kwargs)

    wrapper.__wrapped__ = func
    return wrapper

def _variable_checker(typ):
    def wrapper(x):
        from typed.mods.core import type, isterm
        # Replaced isinstance with framework isterm
        if not isterm(x, typ):
            raise TypeErr(term=typ, arg=None, expected=typ, received=type(x), message="Mismatch type in variable value.")
        return x
    return wrapper

def _get_dom_cod(func_obj):
    from typed.mods.types.base import TYPE
    from inspect import Signature
    from typed.mods.core import type

    if hasattr(func_obj, "dom") and hasattr(func_obj, "cod"):
        dom_val = func_obj.dom
        dom = tuple(dom_val) if hasattr(dom_val, '__iter__') and not isinstance(dom_val, str) else (dom_val,)
        cod = func_obj.cod
        if not isinstance(cod, TYPE):
            raise CodErr(term=func_obj, expected=TYPE, received=type(cod), message="attribute 'cod' is not a TYPE")
        return dom, cod

    orig = getattr(func_obj, "func", func_obj)
    dom = tuple(_hinted_domain(orig))
    cod = _hinted_codomain(orig)
    if cod is Signature.empty or not isinstance(cod, TYPE):
        raise CodErr(term=func_obj, expected=TYPE, received=type(cod), message="missing or non-TYPE codomain annotation")
    return dom, cod
