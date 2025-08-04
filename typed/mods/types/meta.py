import re
import inspect

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
    def __instancecheck__(cls, instance):
        return isinstance(instance, type) and issubclass(instance, type)

class _Callable(type):
    def __instancecheck__(cls, instance):
        if issubclass(type(instance), cls):
            return True

        unwrapped_instance = instance
        while hasattr(unwrapped_instance, 'func') and unwrapped_instance.func is not unwrapped_instance:
            unwrapped_instance = unwrapped_instance.func
        return (
            inspect.isbuiltin(instance)  or
            inspect.ismethod(instance)   or
            inspect.isfunction(instance) or
            inspect.isclass(instance)
        )

class _Builtin(_Callable):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            if issubclass(type(instance), cls):
                return True
            unwrapped_instance = instance.func if hasattr(instance, 'func') else instance
            return inspect.isbuiltin(unwrapped_instance)
        return False

class _Method(_Callable):
    def __instancecheck_(cls, instance):
        return inspect.ismethod(instance)

class _Lambda(_Callable):
    def __instancecheck__(cls, instance):
        return (
            inspect.isfunction(instance)    and
            instance.__name__ == '<lambda>' and
            not inspect.ismethod(instance)  and
            not inspect.isbuiltin(instance)
        )

class _Function(_Callable):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            if issubclass(type(instance), cls):
                return True
            unwrapped_instance = instance.func if hasattr(instance, 'func') else instance

            return (
                inspect.isfunction(unwrapped_instance) and
                unwrapped_instance.__name__ != '<lambda>' and
                not inspect.ismethod(unwrapped_instance) and
                not inspect.isbuiltin(unwrapped_instance)
            )
        return False

class _CompFuncType(_Function):
    pass

class _HintedDomFuncType(_CompFuncType):
    def __instancecheck__(cls, instance):
        if issubclass(type(instance), cls):
            return True

        if not super().__instancecheck__(instance):
            return False
        from typed.mods.helper.helper import _is_domain_hinted
        try:
            return _is_domain_hinted(instance.func)
        except Exception:
            return False

class _HintedCodFuncType(_CompFuncType):
    def __instancecheck__(cls, instance):
        if issubclass(type(instance), cls):
            return True

        if not super().__instancecheck__(instance):
            return False
        from typed.mods.helper.helper import _is_codomain_hinted
        try:
            return _is_codomain_hinted(instance.func)
        except Exception:
            return False

class _HintedFuncType(_HintedCodFuncType, _HintedDomFuncType): pass
class _TypedDomFuncType(_HintedDomFuncType): pass
class _TypedCodFuncType(_HintedCodFuncType): pass
class _TypedFuncType(_HintedFuncType, _TypedDomFuncType, _TypedCodFuncType): pass
