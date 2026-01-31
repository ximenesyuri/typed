import inspect
from typed.mods.meta.base import _TYPE_
from typed.mods.helper.helper import _name, _issubtype

class CALLABLE(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE
        if _issubtype(TYPE(instance), cls):
            return True
        unwrapped = instance
        while hasattr(unwrapped, 'func') and unwrapped.func is not unwrapped:
            unwrapped = unwrapped.func
        return (
            inspect.isbuiltin(instance)
            or inspect.ismethod(instance)
            or inspect.isfunction(instance)
            or inspect.isclass(instance)
        )

class GENERATOR(_TYPE_):
    def __instancecheck__(cls, instance):
        return (
            inspect.isgeneratorfunction(instance)
            or inspect.isasyncgenfunction(instance)
        )

class BUILTIN(CALLABLE):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            from typed.mods.types.base import TYPE
            if _issubtype(TYPE(instance), cls):
                return True
            unwrapped = instance.func if hasattr(instance, 'func') else instance
            return inspect.isbuiltin(unwrapped)
        return False

class CLASS(CALLABLE):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            from typed.mods.types.base import TYPE
            if _issubtype(TYPE(instance), cls):
                return True
            return inspect.isclass(instance)
        return False

class BOUND_METHOD(CALLABLE):
    def __instancecheck__(cls, instance):
        return inspect.ismethod(instance) and instance.__self__ is not None

class UNBOUND_METHOD(CALLABLE):
    def __instancecheck__(cls, instance):
        return inspect.isfunction(instance) and '.' in getattr(instance, '__qualname__', '')

class METHOD(CALLABLE):
    def __instancecheck__(cls, instance):
        return (
            inspect.ismethod(instance) and instance.__self__ is not None
            or inspect.isfunction(instance) and '.' in getattr(instance, '__qualname__', '')
        )

class LAMBDA(CALLABLE):
    def __instancecheck__(cls, instance):
        return (
            inspect.isfunction(instance)
            and instance.__name__ == '<lambda>'
            and not inspect.ismethod(instance)
            and not inspect.isbuiltin(instance)
        )

class FUNCTION(CALLABLE):
    """
    Build the 'function type' of functions with
    a given number of argumens:
        > the objects of 'Function(n, m)' are functions
        > with exactly 'n>=0' pos arguments and 'm>=' kwargs.
        > For 'n<0' and 'm<0' any function is in 'Function(n, m)'
    """
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            from typed.mods.types.base import TYPE
            if _issubtype(TYPE(instance), cls):
                return True
            unwrapped = instance.func if hasattr(instance, 'func') else instance
            return (
                inspect.isfunction(unwrapped)
                and unwrapped.__name__ != '<lambda>'
                and not inspect.ismethod(unwrapped)
                and not inspect.isbuiltin(unwrapped)
            )

    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args) > 2:
            raise AttributeError(
                "Wrong number of args in Function:\n"
                " ==> received more args than expected\n"
                "     [expected_args] n<=2\n"
               f"     [received_args] {len(args)}"
            )
        if len(args) <= 2:
            for arg in args:
                if not isinstance(arg, int):
                    raise AttributeError(
                        "Wrong type in Function:\n"
                       f" ==> '{_name(arg)}': has unexpected type\n"
                        "     [expected_type] Int\n"
                       f"     [received_type] {_name(type(arg))}"
                    )

        class_name = f'Function({args})'
        from typed.mods.types.func import Function
        return FUNCTION(class_name, (Function,), {'__display__': class_name})

class COMPOSABLE(FUNCTION):
    def __instancecheck__(cls, instance):
        super().__instancecheck__(instance)

class PARTIAL(FUNCTION):
    def __instancecheck__(cls, instance):
        return getattr(instance, 'is_partial', False)

class HINTED_DOM(PARTIAL, COMPOSABLE):
    """
    Build the 'hinted-domain function type' of types:
        > the objects of 'HintedDom(X, Y, ...)'
        > are objects 'f(x: X, y: Y, ...)' of 'HintedDom'
    The case 'HintedDom(n, m)' is the restriction of
    'Function(n, m)' to 'HintedDom'
    """
    def __instancecheck__(cls, instance):
        if issubclass(type(instance), cls):
            return True
        if not super().__instancecheck__(instance):
            return False
        from typed.mods.helper.helper import _is_domain_hinted
        try:
            return _is_domain_hinted(instance.func)
        except:
            return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.base  import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int):
            from typed.mods.parametric.func  import _HintedDom_
            return _HintedDom_(args[0])
        if args and all(isinstance(t, TYPE) for t in args) and not kwargs:
            from typed.mods.parametric.func  import _HintedDom_
            return _HintedDom_(*args, **kwargs)
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types")

class HINTED_COD(PARTIAL, COMPOSABLE):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE
        if _issubtype(TYPE(instance), cls):
            return True
        if not super().__instancecheck__(instance):
            return False
        from typed.mods.helper.helper import _is_codomain_hinted
        try:
            return _is_codomain_hinted(instance.func)
        except:
            return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.base  import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int):
            from typed.mods.parametric.func  import _HintedCod_
            return _HintedCod_(args[0])
        if len(args)==1 and isinstance(args[0], TYPE):
            from typed.mods.parametric.func  import _HintedCod_
            return _HintedCod_(args[0])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or a single type")

class HINTED(HINTED_COD, HINTED_DOM):
    def __instancecheck__(cls, instance):
        return super().__instancecheck__(instance)

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.base  import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int) and not kwargs:
            from typed.mods.parametric.func  import _Hinted_
            return _Hinted_(args[0])
        if 'cod' in kwargs and all(isinstance(t, TYPE) for t in args):
            from typed.mods.parametric.func  import _Hinted_
            return _Hinted_(*args, cod=kwargs['cod'])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types+cod=Type")

class TYPED_DOM(HINTED_DOM):
    def __instancecheck__(cls, instance):
        return super().__instancecheck__(instance)

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.base  import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int):
            from typed.mods.parametric.func  import _TypedDom_
            return _TypedDom_(args[0])
        if args and all(isinstance(t, TYPE) for t in args) and not kwargs:
            from typed.mods.parametric.func  import _TypedDom_
            return _TypedDom_(*args)
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types")

class TYPED_COD(HINTED_COD):
    def __instancecheck__(cls, instance):
        return super().__instancecheck__(instance)

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.base  import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int):
            from typed.mods.parametric.func  import _TypedCod_
            return _TypedCod_(args[0])
        if len(args)==1 and isinstance(args[0], TYPE):
            from typed.mods.parametric.func  import _TypedCod_
            return _TypedCod_(args[0])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or a single type")

class TYPED(HINTED, TYPED_DOM, TYPED_COD):
    def __instancecheck__(cls, instance):
        if getattr(instance, "is_lazy", False):
            wrapped = getattr(instance, "_wrapped", None)
            if wrapped is None:
                return False
            return isinstance(wrapped, cls)

        return super().__instancecheck__(instance)

    def check(self, instance):
        if hasattr(self, "__types__"):
            from typed.mods.helper.helper import _hinted_domain, _hinted_codomain
            domain_hints = set(_hinted_domain(instance))
            return_hint = _hinted_codomain(instance)
            return domain_hints == set(self.__types__) and return_hint == self.__codomain__
        return True

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.func import Typed
        if cls is Typed or issubclass(cls, Typed):
            if len(args) == 1 and inspect.isfunction(args[0]) and not isinstance(args[0], Typed):
                return type.__call__(Typed, args[0])
        from typed.mods.types.base import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int) and not kwargs:
            from typed.mods.parametric.func  import _Typed_
            return _Typed_(args[0])
        if 'cod' in kwargs and all(isinstance(t, TYPE) for t in args):
            from typed.mods.parametric.func  import _Typed_
            return _Typed_(*args, cod=kwargs['cod'])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types+cod=Type")

class CONDITION(TYPED):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import Bool
        return super().__instancecheck__(instance) and instance.cod is Bool

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.func import Condition
        if cls is Condition or issubclass(cls, Condition):
            if len(args) == 1 and inspect.isfunction(args[0]) and not isinstance(args[0], Condition):
                from typed.mods.types.base import Bool
                typed = super().__call__(args[0])
                if typed.cod is not Bool:
                    from typed.mods.types.base import TYPE
                    raise TypeError(
                        f"Wrong type in codomain of '{_name(args[0])}':\n"
                        f" ==> '{_name(typed.cod)}' is not 'Bool'"
                    )
                return type.__call__(Condition, args[0])
        from typed.mods.types.base import TYPE
        if all(isinstance(t, TYPE) for t in args):
            from typed.mods.parametric.func  import _Condition_
            return _Condition_(*args)

class FACTORY(TYPED):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import Typed
        if instance == Typed.__call__:
            return True
        return isinstance(instance, Typed) and _issubtype(instance.cod, TYPE)

class OPERATION(FACTORY):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE, Tuple
        return super().__instancecheck__(instance) and _issubtype(instance.dom, Tuple(TYPE))

class DEPENDENT(FACTORY):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance) and hasattr(instance, "is_dependent_type"):
            return instance.is_dependent_type
        return False

class LAZY(HINTED):
    def __instancecheck__(cls, instance):
        if not getattr(instance, "is_lazy", False):
            return False
        return getattr(instance, "_wrapped", None) is None
