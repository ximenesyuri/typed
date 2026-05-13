def _from_typing(obj):
    try:
        from typing import Any as Any_, NoReturn, Final
        if obj is Any_ or obj is NoReturn or obj is Final:
            return True
    except Exception:
        pass
    if hasattr(obj, "__module__") and obj.__module__ == "typing":
        return True
    if getattr(type(obj), "__module__", None) == "typing":
        return True
    return False


def _inner_union(*types):
    class _union_meta(type):
        def __instancecheck__(cls, instance):
            return isinstance(instance, tuple(cls.__types__))

    return _union_meta("Inner Union", (), {'__types__': types})

def _inner_dict_union(*types):
    class _union_meta(type):
        def __instancecheck__(cls, instance):
            from typed.mods.types.base import TYPE
            for t in cls.__types__:
                if isinstance(t, TYPE) and hasattr(t, '__instancecheck__'):
                    result = t.__instancecheck__(instance)
                    if result:
                        return True
                else:
                    result = isinstance(instance, t)
                    if result:
                        return True
            return False
    return _union_meta("Inner Union", (), {'__types__': types})


def _META(name, bases, instancecheck, subclasscheck=None, **attrs):
    dct = {'__instancecheck__': staticmethod(instancecheck)}
    if subclasscheck:
        dct['__subclasscheck__'] = staticmethod(subclasscheck)
    dct.update(attrs)
    return type(name, bases, dct)
