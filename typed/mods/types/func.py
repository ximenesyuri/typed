from inspect import signature
from typing import get_type_hints
from typed.mods.helper.func import (
    _unwrap,
    _is_composable,
    _get_args,
    _get_kwargs,
    _get_pos_args,
    _is_domain_hinted,
    _is_codomain_hinted,
    _hinted_domain,
    _hinted_codomain,
    _check_domain,
    _check_codomain,
    _get_dom_cod
)
from typed.mods.helper.general import _name
from typed.mods.meta.func import (
    CALLABLE,
    GENERATOR,
    BUILTIN,
    LAMBDA,
    CLASS,
    BOUND_METHOD,
    UNBOUND_METHOD,
    METHOD,
    FUNCTION,
    ATTR_FUNC,
    DOM_FUNC,
    COD_FUNC,
    COMP_FUNC,
    PARTIAL,
    DOM_HINTED,
    COD_HINTED,
    HINTED,
    DOM_TYPED,
    COD_TYPED,
    TYPED,
    CONDITION,
    FACTORY,
    OPERATION,
    DEPENDENT,
    LAZY
)

Callable      = CALLABLE('Callable', (), {"__display__": "Callable"})
Generator     = GENERATOR('Generator', (), {"__display__": "Generator"})
Builtin       = BUILTIN('Builtin', (Callable,), {"__display__": "Builtin"})
Lambda        = LAMBDA('Lambda', (Callable,), {"__display__": "Lambda"})
Class         = CLASS('Class', (Callable,), {"__display__": "Class"})
BoundMethod   = BOUND_METHOD('BoundMethod', (Callable,), {"__display__": "BoundMethod"})
UnboundMethod = UNBOUND_METHOD('UnboundMethod', (Callable,), {"__display__": "UnboundMethod"})
Method        = METHOD('Method', (Callable,), {"__display__": "Method"})

class Function(Callable, metaclass=FUNCTION):
    @property
    def args(self):
        return _get_args(self)

    @property
    def kwargs(self):
        return _get_kwargs(self)

    @property
    def posargs(self):
        return _get_pos_args(self)

    def unwrap(self):
        return _unwrap(self)


AttrFunc = ATTR_FUNC('AttrFunc', (Function,), {"__display__": "AttrFunc"})
DomFunc  = DOM_FUNC('DomFunc', (Function,), {"__display__": "DomFunc"})
CodFunc  = COD_FUNC('CodFunc', (Function,), {"__display__": "CodFunc"})

class CompFunc(DomFunc, CodFunc, metaclass=COMP_FUNC):
    def __rlshift__(self, other):
        """
        Support 'other << self' when 'other' does not
        implement __lshift__ but is in DomFunc/CodFunc.
        """
        return CompFunc.__lshift__(other, self)

    def __rrshift__(self, other):
        """
        Support 'other >> self' when 'other' does not
        implement __rshift__ but is in DomFunc/CodFunc.
        """
        return CompFunc.__rshift__(other, self)

    def __lshift__(self, other):
        """
        (f << g)(*args, **kwargs) == f(g(*args, **kwargs)).
        """
        if not _is_composable(other, self):
            dom_f, cod_f = _get_dom_cod(self)
            dom_g, cod_g = _get_dom_cod(other)
            dom0_f = dom_f[0] if dom_f else None
            raise TypeError(
                "Wrong type in function composition 'f << g':\n"
                f" ==> codomain '{_name(cod_g)}' of '{_name(other)}' "
                f"does not match domain '{_name(dom0_f)}' of '{_name(self)}'"
            )

        dom_f, cod_f = _get_dom_cod(self)
        dom_g, cod_g = _get_dom_cod(other)

        if not dom_f:
            raise TypeError(
                "Wrong type in function composition 'f << g':\n"
                f" ==> '{_name(self)}' has empty domain"
            )

        if len(dom_f) > 1:
            cod_types = getattr(cod_g, "__types__", None)
            if cod_types is None or tuple(cod_types) != tuple(dom_f):
                raise TypeError(
                    "Wrong type in function composition 'f << g':\n"
                    f" ==> '{_name(self)}' expects {len(dom_f)} arguments but "
                    f"'{_name(other)}' returns '{_name(cod_g)}'; cannot feed the result "
                    f"of '{_name(other)}' into '{_name(self)}'"
                )

        orig_f = _unwrap(self)
        orig_g = _unwrap(other)

        sig_g = signature(orig_g)
        ann_g = get_type_hints(orig_g)

        composite_anns = dict(ann_g)
        composite_anns["return"] = cod_f

        outer = self
        inner = other

        def composed_orig(*args, **kwargs):
            return outer(inner(*args, **kwargs))

        composed_orig.__name__ = (
            f"{getattr(outer, '__name__', 'f')}∘{getattr(inner, '__name__', 'g')}"
        )
        composed_orig.__annotations__ = composite_anns
        composed_orig.__signature__ = sig_g

        from typed.mods.types.func import Lazy
        if isinstance(self, Lazy) and isinstance(other, Lazy):
            return Lazy(composed_orig)

        return composed_orig

    def __rshift__(self, other):
        """
        (f >> g)(*args, **kwargs) == g(f(*args, **kwargs)).
        """
        if not _is_composable(self, other):
            dom_f, cod_f = _get_dom_cod(self)
            dom_g, cod_g = _get_dom_cod(other)
            dom0_g = dom_g[0] if dom_g else None
            raise TypeError(
                "Wrong type in function composition 'f >> g':\n"
                f" ==> codomain '{_name(cod_f)}' of '{_name(self)}' "
                f"does not match domain '{_name(dom0_g)}' of '{_name(other)}'"
            )

        dom_f, cod_f = _get_dom_cod(self)
        dom_g, cod_g = _get_dom_cod(other)

        if not dom_g:
            raise TypeError(
                "Wrong type in function composition 'f >> g':\n"
                f" ==> '{_name(other)}' has empty domain"
            )

        if len(dom_g) > 1:
            cod_types = getattr(cod_f, "__types__", None)
            if cod_types is None or tuple(cod_types) != tuple(dom_g):
                raise TypeError(
                    "Wrong type in function composition 'f >> g':\n"
                    f" ==> '{_name(other)}' expects {len(dom_g)} arguments but "
                    f"'{_name(self)}' returns '{_name(cod_f)}'; cannot feed the result "
                    f"of '{_name(self)}' into '{_name(other)}'"
                )

        orig_f = _unwrap(self)
        orig_g = _unwrap(other)

        sig_f = signature(orig_f)
        ann_f = get_type_hints(orig_f)

        composite_anns = dict(ann_f)
        composite_anns["return"] = cod_g

        inner = self
        outer = other

        def composed_orig(*args, **kwargs):
            return outer(inner(*args, **kwargs))

        composed_orig.__name__ = (
            f"{getattr(outer, '__name__', 'g')}∘{getattr(inner, '__name__', 'f')}"
        )
        composed_orig.__annotations__ = composite_anns
        composed_orig.__signature__ = sig_f

        from typed.mods.types.func import Lazy
        if isinstance(self, Lazy) and isinstance(other, Lazy):
            return Lazy(composed_orig)

        return composed_orig

class Partial(Function, metaclass=PARTIAL):
    def __init__(self, func, bound_args, bound_kwargs):
        self.original_func = func
        self.func = func
        self.__wrapped__ = func

        self.bound_args = list(bound_args)
        self.bound_kwargs = dict(bound_kwargs)
        self.is_partial = True
        self.is_lazy = getattr(func, "is_lazy", False)

        try:
            from typed.mods.general import _
            base = _unwrap(func)

            def _fmt_arg(a):
                if a is _:
                    return "_"
                return repr(a)

            pos = ", ".join(_fmt_arg(a) for a in bound_args)
            kw  = ", ".join(
                f"{k}={_fmt_arg(v)}" for k, v in bound_kwargs.items()
            )
            inside = ", ".join(p for p in (pos, kw) if p)
            self.__display__ = f"{_name(base)}({inside})"
        except Exception:
            self.__display__ = _name(func)

        if hasattr(func, '__name__'):
            self.__name__ = f"{func.__name__}_partial"
        else:
            self.__name__ = "partial"

        if hasattr(func, 'domain'):
            self._original_domain = func.domain
        if hasattr(func, 'codomain'):
            self._original_codomain = func.codomain

    def __call__(self, *new_args, **new_kwargs):
        from typed.mods.general import _
        from typed.mods.types.base import TYPE

        effective_new_pos = [a for a in new_args if a is not _]
        effective_new_kw  = [v for v in new_kwargs.values() if v is not _]
        num_effective_new = len(effective_new_pos) + len(effective_new_kw)

        expected_remaining = len(self.domain)

        if num_effective_new > expected_remaining:
            if len(new_args) == 1 and not new_kwargs:
                input_val = new_args[0]
            else:
                input_val = tuple(new_args) if not new_kwargs else (tuple(new_args), new_kwargs)

            if len(self.domain) == 1:
                expected_type = self.domain[0]
            else:
                expected_type = self.domain

            actual_type = TYPE(input_val)

            raise TypeError(
                f"Domain mismatch in partial application '{_name(self)}':\n"
                f" ==> input has value '{input_val}'\n"
                f"     [expected_type] '{_name(expected_type)}'\n"
                f"     [received_type] '{_name(actual_type)}'"
            )

        arg_list = list(self.bound_args)
        kwarg_dict = dict(self.bound_kwargs)

        new_args_iter = iter(new_args)
        for i, arg in enumerate(arg_list):
            if arg is _:
                try:
                    arg_list[i] = next(new_args_iter)
                except StopIteration:
                    break

        for extra in new_args_iter:
            arg_list.append(extra)

        target = getattr(self.func, "func", self.func)
        try:
            sig = signature(target)
            param_names = list(sig.parameters.keys())
        except Exception:
            sig = None
            param_names = []

        for kwarg_name, kwarg_value in new_kwargs.items():
            if kwarg_name in kwarg_dict and kwarg_dict[kwarg_name] is not _:
                raise TypeError(
                    f"Argument '{kwarg_name}' is already bound in this partial "
                    f"and cannot be provided again."
                )

            if kwarg_name in param_names:
                param_index = param_names.index(kwarg_name)
                if param_index < len(arg_list) and arg_list[param_index] is not _:
                    raise TypeError(
                        f"Argument '{kwarg_name}' is already bound in this partial "
                        f"and cannot be provided again."
                    )

        if param_names:
            for kwarg_name, kwarg_value in new_kwargs.items():
                if kwarg_name in param_names:
                    param_index = param_names.index(kwarg_name)
                    if param_index < len(arg_list) and arg_list[param_index] is _:
                        arg_list[param_index] = kwarg_value

        if _ in arg_list:
            new_partial = object.__new__(self.__class__)
            new_partial.__init__(self.func, arg_list, kwarg_dict)
            return new_partial

        cleaned_args = [arg for arg in arg_list if arg is not _]

        final_kwargs = kwarg_dict.copy()
        final_kwargs.update(new_kwargs)

        if sig is not None:
            for i in range(min(len(cleaned_args), len(param_names))):
                param_name = param_names[i]
                if param_name in final_kwargs:
                    del final_kwargs[param_name]

        return self.func(*cleaned_args, **final_kwargs)

    def __repr__(self):
        return (
            f"<Partial: {getattr(self.func, '__name__', 'func')} "
            f"with bound args {self.bound_args} and kwargs {self.bound_kwargs}>"
        )

    def __lshift__(self, other):
        return CompFunc.__lshift__(self, other)

    def __rlshift__(self, other):
        return CompFunc.__lshift__(other, self)

    def __rshift__(self, other):
        return CompFunc.__rshift__(self, other)

    def __rrshift__(self, other):
        return CompFunc.__rshift__(other, self)

    @property
    def domain(self):
        from typed.mods.general import _
        if not hasattr(self, '_original_domain'):
            return ()

        target = getattr(self.func, "func", self.func)

        try:
            sig = signature(target)
            param_names = list(sig.parameters.keys())
        except Exception:
            remaining = [
                t for arg, t in zip(self.bound_args, self._original_domain)
                if arg is _
            ]
            return tuple(remaining)

        remaining_types = []

        for idx, (name, typ) in enumerate(zip(param_names, self._original_domain)):
            pos_bound = idx < len(self.bound_args) and self.bound_args[idx] is not _
            kw_bound = name in self.bound_kwargs

            if not pos_bound and not kw_bound:
                remaining_types.append(typ)

        return tuple(remaining_types)

    @property
    def codomain(self):
        if hasattr(self, '_original_codomain'):
            return self._original_codomain
        return None

    @property
    def dom(self):
        return self.domain

    @property
    def cod(self):
        return self.codomain


class DomHinted(DomFunc, Partial, metaclass=DOM_HINTED):
    def __init__(self, func):
        _is_domain_hinted(func)
        self.func = func
        self.is_partial = False
        self._hinted_domain = _hinted_domain(self.func)

    @property
    def domain(self):
        return self._hinted_domain

    @property
    def dom(self):
        return self.domain

    def __repr__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        return f"<DomHinted: {self.__name__}({ds})>"
    def __str__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        return f"{self.__name__}({ds})"

class CodHinted(CodFunc, Partial, metaclass=COD_HINTED):
    def __init__(self, func):
        _is_codomain_hinted(func)
        self.func = func
        self.is_partial = False
        self._hinted_codomain = _hinted_codomain(self.func)

    @property
    def codomain(self):
        return self._hinted_codomain

    @property
    def cod(self):
        return self.codomain

    def __repr__(self):
        c = self.codomain.__name__
        return f"<CodHinted: {self.__name__} -> {c}>"

    def __str__(self):
        c = self.codomain.__name__
        return f"{self.__name__} -> {c}"

class Hinted(CompFunc, DomHinted, CodHinted, metaclass=HINTED):
    def __init__(self, func):
        _is_domain_hinted(func)
        _is_codomain_hinted(func)
        DomHinted.__init__(self, func)
        CodHinted.__init__(self, func)

    @property
    def domain(self):
        return self._hinted_domain
    @property
    def dom(self):
        return self.domain
    @property
    def codomain(self):
        return self._hinted_codomain
    @property
    def cod(self):
        return self.codomain

class DomTyped(DomHinted, metaclass=DOM_TYPED):
    def __call__(self, *args, **kwargs):
        sig = signature(self.func)
        b = sig.bind(*args, **kwargs); b.apply_defaults()
        _check_domain(self.func, list(b.arguments.keys()), self.domain, None, list(b.arguments.values()))
        return self.func(*b.args, **b.kwargs)
    def __repr__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        return f"<DomTyped: {self.__name__}({ds}) runtime-checked>"
    def __str__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        return f"{self.__name__}({ds})!!"

class CodTyped(CodHinted, metaclass=COD_TYPED):
    def __call__(self, *args, **kwargs):
        sig = signature(self.func)
        b = sig.bind(*args, **kwargs); b.apply_defaults()
        r = self.func(*b.args, **b.kwargs)
        from typed.mods.types.base import TYPE
        _check_codomain(self.func, _hinted_codomain(self.func), TYPE(r), r)
        return r
    def __repr__(self):
        c = self.codomain.__name__
        return f"<CodTyped: {self.__name__} -> {c} runtime-checked>"
    def __str__(self):
        c = self.codomain.__name__
        return f"{self.__name__} -> {c}!"

class Typed(Hinted, DomTyped, CodTyped, metaclass=TYPED):
    def __call__(self, *args, **kwargs):
        from typed.mods.general import _
        has_underscore = (_ in args) or any(v is _ for v in kwargs.values())
        if has_underscore:
            partial_instance = object.__new__(Partial)
            partial_instance.__init__(self, args, kwargs)
            return partial_instance
        sig = signature(self.func)
        b = sig.bind(*args, **kwargs)
        b.apply_defaults()
        _check_domain(
            self.func,
            list(b.arguments.keys()),
            self.domain,
            None,
            list(b.arguments.values()),
        )
        result = self.func(*b.args, **b.kwargs)
        from typed.mods.types.base import TYPE
        _check_codomain(self.func, _hinted_codomain(self.func), TYPE(result), result)
        return result
    def __repr__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        cs = self.codomain.__name__
        return f"<Typed: {self.__name__}({ds}) -> {cs} runtime-checked>"
    def __str__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        cs = self.codomain.__name__
        return f"{self.__name__}({ds})! -> {cs}!"

Condition = CONDITION("Condition", (Typed,), {
    "__display__": "Condition"
})

Factory = FACTORY("Factory", (Typed,), {
    "__display__": "Factory"
})

Operation = OPERATION("Operation", (Factory,), {
    "__display__": "Operation"
})

Dependent = DEPENDENT("Dependent", (Factory,), {
    "__display__": "Dependent"
})

class Lazy(Hinted, metaclass=LAZY):
    def __init__(self, f):
        self.func = f
        self.__wrapped__ = f

        self._wrapped = None
        self.is_lazy = True

        self._lazy_domain = tuple(_hinted_domain(self.func))
        self._lazy_codomain = _hinted_codomain(self.func)

    @property
    def domain(self):
        return self._lazy_domain

    @property
    def dom(self):
        return self.domain

    @property
    def codomain(self):
        return self._lazy_codomain

    @property
    def cod(self):
        return self.codomain

    def materialize(self):
        if self._wrapped is None:
            self._wrapped = Typed(self.func)
        return self._wrapped

    def __call__(self, *a, **kw):
        from typed.mods.general import _
        has_underscore = (_ in a) or any(v is _ for v in kw.values())
        if has_underscore:
            p = object.__new__(Partial)
            p.__init__(self, a, kw)
            return p

        return self.materialize()(*a, **kw)

    def __getattr__(self, name):
        return getattr(self.materialize(), name)

    def __repr__(self):
        return f"<Lazy for {getattr(self.func, '__name__', 'anonymous')}>"
