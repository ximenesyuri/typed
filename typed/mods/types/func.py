import inspect
from typed.mods.helper.helper import (
    _is_domain_hinted,
    _is_codomain_hinted,
    _hinted_domain,
    _hinted_codomain,
    _check_domain,
    _check_codomain,
    _get_args,
    _get_kwargs,
    _get_pos_args,
    _name,
)
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
    PARTIAL,
    COMPOSABLE,
    HINTED_DOM,
    HINTED_COD,
    HINTED,
    TYPED_DOM,
    TYPED_COD,
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

class Underscore:
    def __repr__(self):
        return "_"

    def __str__(self):
        return "_"

_ = Underscore()

class Partial(Function, metaclass=PARTIAL):
    def __init__(self, original_func, bound_args, bound_kwargs):
        self.original_func = original_func
        self.bound_args = list(bound_args)
        self.bound_kwargs = dict(bound_kwargs)
        self.is_partial = True
        self.is_lazy = getattr(original_func, "is_lazy", False)
        if hasattr(original_func, '__name__'):
            self.__name__ = f"{original_func.__name__}_partial"
        else:
            self.__name__ = "partial"
        if hasattr(original_func, 'domain'):
            self._original_domain = original_func.domain
        if hasattr(original_func, 'codomain'):
            self._original_codomain = original_func.codomain

    def __call__(self, *new_args, **new_kwargs):
        arg_list = list(self.bound_args)
        kwarg_dict = dict(self.bound_kwargs)

        new_args_iter = iter(new_args)
        for i, arg in enumerate(arg_list):
            if arg is _:
                try:
                    arg_list[i] = next(new_args_iter)
                except StopIteration:
                    break

        import inspect
        target = getattr(self.original_func, "func", self.original_func)
        try:
            sig = inspect.signature(target)
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
            new_partial.__init__(self.original_func, arg_list, kwarg_dict)
            return new_partial

        cleaned_args = [arg for arg in arg_list if arg is not _]

        final_kwargs = kwarg_dict.copy()
        final_kwargs.update(new_kwargs)

        if sig is not None:
            for i in range(min(len(cleaned_args), len(param_names))):
                param_name = param_names[i]
                if param_name in final_kwargs:
                    del final_kwargs[param_name]

        return self.original_func(*cleaned_args, **final_kwargs)

    def __repr__(self):
        return f"<Partial: {getattr(self.original_func, '__name__', 'func')} with bound args {self.bound_args} and kwargs {self.bound_kwargs}>"

    @property
    def domain(self):
        if not hasattr(self, '_original_domain'):
            return ()

        import inspect
        target = getattr(self.original_func, "func", self.original_func)

        try:
            sig = inspect.signature(target)
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

class HintedDom(Composable, Partial, metaclass=HINTED_DOM):
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

class HintedCod(Composable, Partial, metaclass=HINTED_COD):
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

class TypedDom(HintedDom, metaclass=TYPED_DOM):
    def __call__(self, *args, **kwargs):
        sig = inspect.signature(self.func)
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
        sig = inspect.signature(self.func)
        b = sig.bind(*args, **kwargs); b.apply_defaults()
        r = self.func(*b.args, **b.kwargs)
        from typed.mods.types.base import TYPE
        _check_codomain(self.func, _hinted_codomain(self.func), TYPE(r), r)
        return r
    def __repr__(self):
        c = self.codomain.__name__
        return f"<TypedCod: {self.__name__} -> {c} runtime-checked>"
    def __str__(self):
        c = self.codomain.__name__
        return f"{self.__name__} -> {c}!"

class Typed(Hinted, TypedDom, TypedCod, metaclass=TYPED):
    def __call__(self, *args, **kwargs):
        has_underscore = (_ in args) or any(v is _ for v in kwargs.values())
        if has_underscore:
            partial_instance = object.__new__(Partial)
            partial_instance.__init__(self, args, kwargs)
            return partial_instance
        sig = inspect.signature(self.func)
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
    """
    Lazy-typed function wrapper.

    - Holds the original function in self._orig
    - On first call, materializes a Typed wrapper
    - Thereafter forwards all calls/attribute-lookups to the Typed wrapper
    """

    def __init__(self, f):
        self._orig = f          # original Python function
        self._wrapped = None    # will hold a Typed(self._orig)
        self.func = f           # for meta/Hinted inspection
        self.is_lazy = True     # flag used by meta.LAZY.__instancecheck__

    def materialize(self):
        if self._wrapped is None:
            self._wrapped = Typed(self._orig)
        return self._wrapped

    def __call__(self, *a, **kw):
        has_underscore = (_ in a) or any(v is _ for v in kw.values())
        if has_underscore:
            p = object.__new__(Partial)
            p.__init__(self, a, kw)
            return p

        return self.materialize()(*a, **kw)

    def __getattr__(self, name):
        return getattr(self.materialize(), name)

    def __repr__(self):
        return f"<Lazy for {getattr(self._orig, '__name__', 'anonymous')}>"

