import inspect
from typing import get_type_hints
from functools import wraps
from types import FunctionType, LambdaType
from typed.mods.helper import (
    _is_domain_hinted,
    _is_codomain_hinted,
    _hinted_domain,
    _hinted_codomain,
    _runtime_domain,
    _runtime_codomain,
    _check_domain,
    _check_codomain
)

# -----------------------------
#       Plain FuncType
# -----------------------------
class PlainFuncType:
    def __init__(self, func):
        if not inspect.isfunction(func):
            raise TypeError(f"'{func}' is not callable.")
        self.func = func
        self.__name__ = getattr(func, '__name__', 'anonymous')

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __mul__(self, other: 'PlainFuncType') -> 'PlainFuncType':
        if not isinstance(other, PlainFuncType):
            raise TypeError(f"'{other}' is not a valid plain function type.")

        def composed_func(*args, **kwargs):
            inter_result = other.func(*args, **kwargs)
            if inspect.signature(self.func).parameters:
                try:
                    return self.func(inter_result)
                except TypeError:
                    raise TypeError(f"Cannot compose functions: output of '{other.__name__}' does not match input of '{self.__name__}'")
            else:
                return self.func()

        composed_plain_func = PlainFuncType(composed_func)
        composed_plain_func.__name__ = f"({self.__name__} * {other.__name__})"
        return composed_plain_func

    def __repr__(self):
        return f"<PlainFuncType: {self.__name__}>"

    def __str__(self):
        return self.__name__

# -------------------------
#     Hinted FuncType
# -------------------------
class HintedDomFuncType(PlainFuncType):
    def __init__(self, func):
        if inspect.isfunction(func):
            if inspect.signature(func).parameters:
                _is_domain_hinted(func)
            super().__init__(func)
            self._hinted_domain = _hinted_domain(self.func)

    @property
    def domain(self):
        return self._hinted_domain

    def __repr__(self):
        domain_str = ', '.join(getattr(t, '__name__', str(t)) for t in self.domain)
        return f"<HintedDomFuncType: {self.__name__}({domain_str})>"

    def __str__(self):
        domain_str = ', '.join(getattr(t, '__name__', str(t)) for t in self.domain)
        return f"{self.__name__}({domain_str})"

class HintedCodFuncType(PlainFuncType):
    def __init__(self, func):
        _is_codomain_hinted(func)
        super().__init__(func)
        self._hinted_codomain = _hinted_codomain(self.func)

    @property
    def codomain(self):
        return self._hinted_codomain

    def __repr__(self):
        codomain_str = getattr(self.codomain, '__name__', str(self.codomain))
        return f"<HintedCodFuncType: {self.__name__} -> {codomain_str}>"

    def __str__(self):
        codomain_str = getattr(self.codomain, '__name__', str(self.codomain))
        return f"{self.__name__} -> {codomain_str}"

class HintedFuncType(HintedDomFuncType, HintedCodFuncType):
    def __init__(self, func):
        _is_domain_hinted(func)
        _is_codomain_hinted(func)
        HintedDomFuncType.__init__(self, func)
        HintedCodFuncType.__init__(self, func)

    @property
    def domain(self):
        return self._hinted_domain

    @property
    def codomain(self):
        return self._hinted_codomain

    def __mul__(self, other):
        if not isinstance(other, HintedFuncType):
            raise TypeError(f"'{other}' is not a valid hinted function type.")

        g_codomain = other.codomain
        f_domain = self.domain

        if len(f_domain) != 1 or not (isinstance(g_codomain, type) or hasattr(g_codomain, '__instancecheck__')):
            raise TypeError(f"Composition requires '{self.__name__}' to have a single domain parameter and '{other.__name__}' codomain to be a single type-like object.")

        expected_input_type_for_f = f_domain[0]
        compatibility_ok = False
        if isinstance(expected_input_type_for_f, type) and isinstance(g_codomain, type):
            compatibility_ok = issubclass(g_codomain, expected_input_type_for_f)
        compatibility_ok = False
        if isinstance(g_codomain, type) and isinstance(expected_input_type_for_f, type):
            compatibility_ok = issubclass(g_codomain, expected_input_type_for_f)
        elif hasattr(expected_input_type_for_f, '__instancecheck__') and hasattr(g_codomain, '__instancecheck__'):
            if isinstance(g_codomain, type) and isinstance(expected_input_type_for_f, type):
                compatibility_ok = issubclass(g_codomain, expected_input_type_for_f)
            else:
                raise TypeError(f"Cannot perform 'safe' composition between functions with non-standard or incompatible type hints: '{other.__name__}' output '{g_codomain}' vs '{self.__name__}' input '{f_domain[0]}'")


        def composed_func(*args):
            inter_result = other.func(*args)
            return self.func(inter_result)

        class ComposedHintedFunc:
            def __init__(self, f_hinted, g_hinted):
                self.f = f_hinted.func
                self.g = g_hinted.func
                self._domain = g_hinted.domain
                self._codomain = f_hinted.codomain
                self.__name__ = f"({f_hinted.__name__} * {g_hinted.__name__})"

            def __call__(self, *args, **kwargs):
                inter_result = self.g(*args, **kwargs)
                return self.f(inter_result)

            @property
            def domain(self): return self._domain
            @property
            def codomain(self): return self._codomain
            @property
            def func(self): return self

        composed_callable = ComposedHintedFunc(self, other)
        return HintedFuncType(composed_callable)


# ---------------------------
#       Typed FuncType
# ---------------------------
class TypedDomFuncType(HintedDomFuncType):
    def __init__(self, func):
        super().__init__(func)

    def __call__(self, *args, **kwargs):
        sig = inspect.signature(self.func)
        if sig.parameters:
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            _check_domain(self.func, sig, bound_args)
            result = self.func(*bound_args.args, **bound_args.kwargs)
        else:
            if args or kwargs:
                sig = inspect.signature(self.func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                result = self.func(*bound_args.args, **bound_args.kwargs)
            else:
                result = self.func()
        return result

    def __repr__(self):
        domain_str = ', '.join(getattr(t, '__name__', str(t)) for t in self.domain)
        return f"<TypedDomFuncType: {self.__name__}({domain_str}) dynamic-runtime-checked>"

    def __str__(self):
        domain_str = ', '.join(getattr(t, '__name__', str(t)) for t in self.domain)
        return f"{self.__name__}({domain_str})!!"

class TypedCodFuncType(HintedCodFuncType):
    def __init__(self, func):
        super().__init__(func)

    def __call__(self, *args, **kwargs):
        try:
            sig = inspect.signature(self.func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            result = self.func(*bound_args.args, **bound_args.kwargs)

        except Exception as e:
            raise e

        actual_codomain = type(result)
        _check_codomain(self.func, self._codomain_hint_for_check, actual_codomain, result)

        return result

    def __repr__(self):
        codomain_str = getattr(self.codomain, '__name__', str(self.codomain))
        return f"<TypedCodFuncType: {self.__name__} -> {codomain_str} runtime-checked>"

    def __str__(self):
        codomain_str = getattr(self.codomain, '__name__', str(self.codomain))
        return f"{self.__name__} -> {codomain_str}!"

class TypedFuncType(HintedFuncType, TypedDomFuncType, TypedCodFuncType):
    def __init__(self, func):
        PlainFuncType.__init__(self, func)
        HintedDomFuncType.__init__(self, func)
        HintedCodFuncType.__init__(self, func)
        try:
            sig = inspect.signature(self.func)
            self._param_names = list(sig.parameters.keys())
            if not hasattr(self, '_hinted_domain'):
                self._hinted_domain = _hinted_domain(self.func)
            self._domain_hints_for_check = self._hinted_domain
        except ValueError:
            self._param_names = []
            self._hinted_domain = ()
            self._domain_hints_for_check = ()

        if not hasattr(self, '_hinted_codomain'):
            self._hinted_codomain = _hinted_codomain(self.func)
        self._codomain_hint_for_check = self._hinted_codomain

    def __call__(self, *args, **kwargs):
        sig = inspect.signature(self.func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        actual_domain_values = list(bound_args.arguments.values())
        param_names_in_call_order = list(bound_args.arguments.keys())
        if sig.parameters:
            _check_domain(
                self.func,
                param_names_in_call_order,
                self._domain_hints_for_check,
                None,
                actual_domain_values
            )

        result = self.func(*bound_args.args, **bound_args.kwargs)
        if not hasattr(self, '_codomain_hint_for_check'):
            raise AttributeError(f"'{self.__name__}': missing __codomain__ type hints.")

        actual_codomain = type(result)
        _check_codomain(self.func, self._codomain_hint_for_check, actual_codomain, result)

        return result

    def __mul__(self, other):
        if not isinstance(other, TypedFuncType):
            raise TypeError(f"'{other}' is not a valid typed function type for composition.")

        g_codomain = other.codomain
        f_domain = self.domain

        if len(f_domain) != 1:
            raise TypeError(f"Composition requires '{self.__name__}' to have a single domain parameter.")

        expected_input_type_for_f = f_domain[0]

        if isinstance(g_codomain, type) and isinstance(expected_input_type_for_f, type):
            if not issubclass(g_codomain, expected_input_type_for_f):
                raise TypeError(
                    f"Cannot perform composition: Output of '{other.__name__}' ({g_codomain}) "
                    f"does not match input of '{self.__name__}' ({expected_input_type_for_f})."
                )

        import inspect
        from functools import wraps

        other_sig = inspect.signature(other.func)
        annots = {}
        for ((name, param), domain_type) in zip(other_sig.parameters.items(), other.domain):
            annots[name] = domain_type
        annots['return'] = self.codomain

        @wraps(self.func)
        def composed_runtime_checked_func(*args, **kwargs):
            inter_result = other.func(*args, **kwargs)
            return self.func(inter_result)

        composed_runtime_checked_func.__annotations__ = annots
        composed_runtime_checked_func.__name__ = f"({self.__name__} * {other.__name__})"

        return TypedFuncType(composed_runtime_checked_func) 

    @property
    def domain(self):
        return self._hinted_domain

    @property
    def codomain(self):
        return self._hinted_codomain

    def __repr__(self):
        domain_str = ', '.join(getattr(t, '__name__', str(t)) for t in self.domain)
        codomain_str = getattr(self.codomain, '__name__', str(self.codomain))
        return f"<TypedFuncType: {self.__name__}({domain_str}) -> {codomain_str} runtime-checked>"

    def __str__(self):
        domain_str = ', '.join(getattr(t, '__name__', str(t)) for t in self.domain)
        codomain_str = getattr(self.codomain, '__name__', str(self.codomain))
        return f"{self.__name__}({domain_str})! -> {codomain_str}!"

class BoolFuncType(TypedFuncType):
    def __init__(self, func):
        super().__init__(func)

        if self.codomain is not bool:
            raise TypeError(f"'{self.__name__}' does not have 'bool' as its return type hint.")

    def __repr__(self):
        domain_str = ', '.join(getattr(t, '__name__', str(t)) for t in self.domain)
        return f"<BoolFuncType: {self.__name__}({domain_str}) -> bool runtime-checked>"

    def __str__(self):
        domain_str = ', '.join(getattr(t, '__name__', str(t)) for t in self.domain)
        return f"{self.__name__}({domain_str})! -> bool!"

# ---------------------------
#       Displays
# ---------------------------

PlainFuncType.__display__     = "PlainFuncType"
HintedDomFuncType.__display__ = "HintedDomFuncType"
HintedCodFuncType.__display__ = "HintedCodFuncType"
HintedFuncType.__display__    = "HintedFuncType"
TypedDomFuncType.__display__  = "TypedDomFuncType"
TypedCodFuncType.__display__  = "TypedCodFuncType"
TypedFuncType.__display__     = "TypedFuncType"
BoolFuncType.__display__      = "BoolFuncType"
