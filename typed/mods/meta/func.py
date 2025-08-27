import inspect

class CALLABLE(type):
    def __instancecheck__(cls, instance):
        if issubclass(type(instance), cls):
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

class BUILTIN(CALLABLE):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            if issubclass(type(instance), cls):
                return True
            unwrapped = instance.func if hasattr(instance, 'func') else instance
            return inspect.isbuiltin(unwrapped)
        return False

class BOUND_METHOD(CALLABLE):
    def __instancecheck__(cls, instance):
        return inspect.ismethod(obj) and obj.__self__ is not None

class UNBOUND_METHOD(CALLABLE):
    def __instancecheck__(cls, instance):
        return inspect.isfunction(obj) and '.' in getattr(obj, '__qualname__', '')

class METHOD(CALLABLE):
    def __instancecheck__(cls, instance):
        return (
            inspect.ismethod(obj) and obj.__self__ is not None
            or inspect.isfunction(obj) and '.' in getattr(obj, '__qualname__', '')
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
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            if issubclass(type(instance), cls):
                return True
            unwrapped = instance.func if hasattr(instance, 'func') else instance
            return (
                inspect.isfunction(unwrapped)
                and unwrapped.__name__ != '<lambda>'
                and not inspect.ismethod(unwrapped)
                and not inspect.isbuiltin(unwrapped)
            )
        return False

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

        from typed.mods.factories.func import _Function_
        return _Function_(*args)

class COMPOSABLE(FUNCTION):
    pass

class HINTED_DOM(COMPOSABLE):
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
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], int):
            from typed.mods.factories.func import HintedDom_ as _ff
            return _ff(args[0])
        if args and all(isinstance(t, type) for t in args) and not kwargs:
            from typed.mods.factories.func import _HintedDom_
            return _HintedDom_(*args, **kwargs)
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types")

class HINTED_COD(COMPOSABLE):
    def __instancecheck__(cls, instance):
        if issubclass(type(instance), cls):
            return True
        if not super().__instancecheck__(instance):
            return False
        from typed.mods.helper.helper import _is_codomain_hinted
        try:
            return _is_codomain_hinted(instance.func)
        except:
            return False

    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], int):
            from typed.mods.factories.func import _HintedCod_
            return _HintedCod_(args[0])
        if len(args)==1 and isinstance(args[0], type):
            from typed.mods.factories.func import HintedCod_
            return _HintedCod_(args[0])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or a single type")

class HINTED(HINTED_COD, HINTED_DOM):
    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], int) and not kwargs:
            from typed.mods.factories.func import _Hinted_
            return _Hinted_(args[0])
        if 'cod' in kwargs and all(isinstance(t, type) for t in args):
            from typed.mods.factories.func import _Hinted_
            return _Hinted_(*args, cod=kwargs['cod'])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types+cod=Type")

class TYPED_DOM(HINTED_DOM):
    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], int):
            from typed.mods.factories.func import _TypedDom_
            return _TypedDom_(args[0])
        if args and all(isinstance(t, type) for t in args) and not kwargs:
            from typed.mods.factories.func import _TypedDom_
            return _TypedDom_(*args)
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types")

class TYPED_COD(HINTED_COD):
    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], int):
            from typed.mods.factories.func import _TypedCod_
            return _TypedCod_(args[0])
        if len(args)==1 and isinstance(args[0], type):
            from typed.mods.factories.func import _TypedCod_
            return _TypedCod_(args[0])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or a single type")

class TYPED(HINTED, TYPED_DOM, TYPED_COD):
    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], int) and not kwargs:
            from typed.mods.factories.func import _Typed_
            return _Typed_(args[0])
        if 'cod' in kwargs and all(isinstance(t, type) for t in args):
            if kwargs['cod'] is bool:
                from typed.mods.factories.func import _Condition_
                return _Condition_(*args)
            from typed.mods.factories.func import _Typed_
            return _Typed_(*args, cod=kwargs['cod'])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types+cod=Type")
