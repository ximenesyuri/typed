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
from typed.mods.meta.func import (
    CALLABLE,
    BUILTIN,
    LAMBDA,
    BOUND_METHOD,
    UNBOUND_METHOD,
    METHOD,
    FUNCTION,
    COMPOSABLE,
    HINTED_DOM,
    HINTED_COD,
    HINTED,
    TYPED_DOM,
    TYPED_COD,
    TYPED,
)

Callable      = CALLABLE('Callable', (), {"__display__": "Callable"})
Builtin       = BUILTIN('Builtin', (Callable,), {"__display__": "Builtin"})
Lambda        = LAMBDA('Lambda', (Callable,), {"__display__": "Lambda"})
Function      = FUNCTION('Function', (Callable,), {"__display__": "Function"})
BoundMethod   = BOUND_METHOD('BoundMethod', (Callable,), {"__display__": "BoundMethod"})
UnboundMethod = UNBOUND_METHOD('UnboundMethod', (Callable,), {"__display__": "UnboundMethod"})
Method        = METHOD('Method', (Callable,), {"__display__": "Method"})

setattr(Function, 'args', property(_get_args))
setattr(Function, 'kwargs', property(_get_kwargs))
setattr(Function, 'posargs', property(_get_pos_args))

class Composable(Function, metaclass=COMPOSABLE):
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

class HintedDom(Composable, metaclass=HINTED_DOM):
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

class HintedCod(Composable, metaclass=HINTED_COD):
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

class Hinted(HintedDom, HintedCod, metaclass=HINTED):
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

class TypedDom(HintedDom, metaclass=TYPED_DOM):
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

class TypedCod(HintedCod, metaclass=TYPED_COD):
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

class Typed(Hinted, TypedDom, TypedCod, metaclass=TYPED):
    def __repr__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        cs = self.codomain.__name__
        return f"<Typed: {self.__name__}({ds}) -> {cs} runtime-checked>"
    def __str__(self):
        ds = ', '.join(t.__name__ for t in self.domain)
        cs = self.codomain.__name__
        return f"{self.__name__}({ds})! -> {cs}!"

from typed.mods.decorators import typed
from typed.mods.factories.generics import Filter
from typed.mods.types.base import Any, Bool

def _has_var_arg(func: Function) -> Bool:
    signature = inspect.signature(func)
    for param in signature.parameters.values():
        if param.kind == param.VAR_POSITIONAL:
            return True
    return False

def _has_var_kwarg(func: Function) -> Bool:
    signature = inspect.signature(func)
    for param in signature.parameters.values():
        if param.kind == param.VAR_KEYWORD:
            return True
    return False

Condition      = Typed(Any, cod=Bool)
Decorator      = Typed(Function, cod=Function)
TypedDecorator = Typed(Typed, cod=Typed)
VariableFunc   = Filter(Function, typed(_has_var_arg))
KeywordFunc    = Filter(Function, typed(_has_var_kwarg))

Decorator.__diplay__       = "Decorator"
TypedDecorator.__display__ = "TypedDecorator"
VariableFunc.__display__   = "VariableFunc"
KeywordFunc.__display__    = "KeywordFunc"
