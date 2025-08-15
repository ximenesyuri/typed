import inspect
from typing import get_type_hints
from typed.mods.helper.helper import (
    _is_domain_hinted,
    _is_codomain_hinted,
    _hinted_domain,
    _hinted_codomain,
    _get_args,
    _get_kwargs,
    _get_pos_args,
    _name,
)
from typed.mods.types.meta import (
    _Callable,
    _Builtin,
    _Lambda,
    _Method,
    _Function,
    _Composable,
    _HintedDom,
    _HintedCod,
    _Hinted,
    _TypedDom,
    _TypedCod,
    _Typed,
)

Callable = _Callable('Callable', (), {"__display__": "Callable"})
Builtin  = _Builtin('Builtin', (Callable,), {"__display__": "Builtin"})
Lambda   = _Lambda('Lambda', (Callable,), {"__display__": "Lambda"})
Function = _Function('Function', (Callable,), {"__display__": "Function"})

setattr(Function, 'args', property(_get_args))
setattr(Function, 'kwargs', property(_get_kwargs))
setattr(Function, 'posargs', property(_get_pos_args))

class Composable(Function, metaclass=_Composable):
    def __init__(self, func):
        self.func = func
        self.__name__ = getattr(func, '__name__', 'anonymous')
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    def __mul__(self, other):
        if not isinstance(other, Composable):
            raise TypeError(
                "Wrong type in composition of functions:\n"
                f" ==> '{_name(other)}': has unexpected type\n"
                 "      [expected_type] Composable\n"
                f"      [received_type] {_name(type(other))}"
            )
        def composed(*args, **kwargs):
            mid = other.func(*args, **kwargs)
            return self.func(mid) if inspect.signature(self.func).parameters else self.func()
        c = Composable(composed)
        c.__name__ = f"({self.__name__} * {other.__name__})"
        return c
    def __repr__(self):
        return f"<Composable: {self.__name__}>"
    def __str__(self):
        return self.__name__

class HintedDom(Composable, metaclass=_HintedDom):
    def __init__(self, func):
        _is_domain_hinted(func)
        super().__init__(func)
        self._hinted_domain = _hinted_domain(self.func)
    @property
    def domain(self):
        return self._hinted_domain
    @property
    def dom(self):
        return self.domain
    def __repr__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        return f"<HintedDom: {self.__name__}({ds})>"
    def __str__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        return f"{self.__name__}({ds})"

class HintedCod(Composable, metaclass=_HintedCod):
    def __init__(self, func):
        _is_codomain_hinted(func)
        super().__init__(func)
        self._hinted_codomain = _hinted_codomain(self.func)
    @property
    def codomain(self):
        return self._hinted_codomain
    @property
    def cod(self):
        return self.codomain
    def __repr__(self):
        c = self.codomain.__name__
        return f"<HintedCod: {self.__name__} -> {c}>"
    def __str__(self):
        c = self.codomain.__name__
        return f"{self.__name__} -> {c}"

class Hinted(HintedDom, HintedCod, metaclass=_Hinted):
    def __init__(self, func):
        _is_domain_hinted(func)
        _is_codomain_hinted(func)
        HintedDom.__init__(self, func)
        HintedCod.__init__(self, func)
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

import inspect as _ins
from typed.mods.helper.helper import _check_domain, _check_codomain

class TypedDom(HintedDom, metaclass=_TypedDom):
    def __call__(self, *args, **kwargs):
        sig = _ins.signature(self.func)
        b = sig.bind(*args, **kwargs); b.apply_defaults()
        _check_domain(self.func, list(b.arguments.keys()), self.domain, None, list(b.arguments.values()))
        return self.func(*b.args, **b.kwargs)
    def __repr__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        return f"<TypedDom: {self.__name__}({ds}) runtime-checked>"
    def __str__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        return f"{self.__name__}({ds})!!"

class TypedCod(HintedCod, metaclass=_TypedCod):
    def __call__(self, *args, **kwargs):
        sig = _ins.signature(self.func)
        b = sig.bind(*args, **kwargs); b.apply_defaults()
        r = self.func(*b.args, **b.kwargs)
        from typed.mods.helper.helper import _hinted_codomain
        _check_codomain(self.func, _hinted_codomain(self.func), type(r), r)
        return r
    def __repr__(self):
        c = self.codomain.__name__
        return f"<TypedCod: {self.__name__} -> {c} runtime-checked>"
    def __str__(self):
        c = self.codomain.__name__
        return f"{self.__name__} -> {c}!"

class Typed(Hinted, TypedDom, TypedCod, metaclass=_Typed):
    def __repr__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        cs = self.codomain.__name__
        return f"<Typed: {self.__name__}({ds}) -> {cs} runtime-checked>"
    def __str__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        cs = self.codomain.__name__
        return f"{self.__name__}({ds})! -> {cs}!"
