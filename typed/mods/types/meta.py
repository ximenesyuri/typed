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
        return (
            inspect.isbuiltin(instance)  or
            inspect.ismethod(instance)   or
            inspect.isfunction(instance) or
            inspect.isclass(instance)
        )

class _Builtin(_Callable):
    def __instancecheck__(cls, instance):
        return inspect.isbuiltin(instance)

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
        return (
            inspect.isfunction(instance)        and
            not instance.__name__ == '<lambda>' and
            not inspect.ismethod(instance)      and
            not inspect.isbuiltin(instance)
        )
