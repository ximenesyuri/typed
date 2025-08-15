import re
import inspect
from typed.mods.helper.helper import _name

class _Any(type):
    def __instancecheck__(cls, instance):
        return True
    def __subclasscheck__(cls, subclass):
        return True

class _Pattern(type):
    def __instancecheck__(cls, instance):
        if not isinstance(instance, str):
            return False
        try:
            re.compile(instance)
            return True
        except re.error:
            return False
    def __repr__(cls):
        return "Pattern(str): a string valid as Python regex"

class _META(type):
    def __instancecheck__(self, instance):
        return isinstance(instance, type) and issubclass(instance, type)

class _Callable(type):
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

class _Builtin(_Callable):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            if issubclass(type(instance), cls):
                return True
            unwrapped = instance.func if hasattr(instance, 'func') else instance
            return inspect.isbuiltin(unwrapped)
        return False

class _Method(_Callable):
    def __instancecheck__(cls, instance):
        return inspect.ismethod(instance)

class _Lambda(_Callable):
    def __instancecheck__(cls, instance):
        return (
            inspect.isfunction(instance)
            and instance.__name__ == '<lambda>'
            and not inspect.ismethod(instance)
            and not inspect.isbuiltin(instance)
        )

class _Function(_Callable):
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

        from typed.mods.factories.func import Function_
        return _Function(*args)

class _Composable(_Function):
    pass

class _HintedDom(_Composable):
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
            from typed.mods.factories.func import HintedDom_ as _ff
            return _ff(*args)
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types")

class _HintedCod(_Composable):
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
            from typed.mods.factories.func import HintedCod_ as _ff
            return _ff(args[0])
        if len(args)==1 and isinstance(args[0], type):
            from typed.mods.factories.func import HintedCod_ as _ff
            return _ff(args[0])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or a single type")

class _Hinted(_HintedCod, _HintedDom):
    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], int) and not kwargs:
            from typed.mods.factories.func import Hinted_ as _ff
            return _ff(args[0])
        if 'cod' in kwargs and all(isinstance(t, type) for t in args):
            from typed.mods.factories.func import Hinted_ as _ff
            return _ff(*args, cod=kwargs['cod'])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types+cod=Type")

class _TypedDom(_HintedDom):
    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], int):
            from typed.mods.factories.func import TypedDom_ as _ff
            return _ff(args[0])
        if args and all(isinstance(t, type) for t in args) and not kwargs:
            from typed.mods.factories.func import TypedDom_ as _ff
            return _ff(*args)
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types")

class _TypedCod(_HintedCod):
    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], int):
            from typed.mods.factories.func import TypedCod_ as _ff
            return _ff(args[0])
        if len(args)==1 and isinstance(args[0], type):
            from typed.mods.factories.func import TypedCod_ as _ff
            return _ff(args[0])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or a single type")

class _Typed(_Hinted, _TypedDom, _TypedCod):
    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], int) and not kwargs:
            from typed.mods.factories.func import Typed_ as _ff
            return _ff(args[0])
        if 'cod' in kwargs and all(isinstance(t, type) for t in args):
            if kwargs['cod'] is bool:
                from typed.mods.factories.func import Condition_ as _bf
                return _bf(*args)
            from typed.mods.factories.func import Typed_ as _ff
            return _ff(*args, cod=kwargs['cod'])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types+cod=Type")
