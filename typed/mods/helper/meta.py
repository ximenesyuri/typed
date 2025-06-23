import re

class _Union(type):
    def __instancecheck__(cls, instance):
        for t in cls.__types__:
            if isinstance(t, type):
                if hasattr(t, '__instancecheck__'):
                    result = t.__instancecheck__(instance)
                    if result:
                        return True
                else:
                    result = isinstance(instance, t)
                    if result:
                        return True
        return False

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any
        if hasattr(subclass, '__types__') and getattr(cls, '__types__', None) == getattr(subclass, '__types__', None):
            return True

        if subclass is cls:
            return True
        if subclass is Any:
            return True
        if subclass in cls.__types__:
            return True

        for t in cls.__types__:
            if isinstance(t, type):
                if hasattr(t, '__subclasscheck__'):
                    if t.__subclasscheck__(subclass):
                        return True
                else:
                    if issubclass(subclass, t):
                        return True
        return False

class _Prod(type):
    def __instancecheck__(cls, instance):
        if not isinstance(instance, tuple):
            return False
        if len(instance) != len(cls.__types__):
            return False
        return all(isinstance(x, t) for x, t in zip(instance, cls.__types__))

    def check(self, instance):
        if not isinstance(instance, tuple):
            return False
        if len(instance) != len(self.__types__):
            return False
        return all(isinstance(x, t) for x, t in zip(instance, self.__types__))

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any
        if subclass is cls or subclass is Any or issubclass(subclass, tuple):
            return True
        if hasattr(subclass, '__bases__') and tuple in subclass.__bases__ and hasattr(subclass, '__types__') and len(subclass.__types__) == len(cls.__types__):
            return all(issubclass(st, ct) for st, ct in zip(subclass.__types__, cls.__types__))
        return False

class _UProd(type):
    def __instancecheck__(cls, instance):
        if not isinstance(instance, tuple):
            return False

        if len(instance) != len(cls.__types__):
            return False

        type_counts = {typ: cls.__types__.count(typ) for typ in cls.__types__}
        for elem in instance:
            for typ in type_counts:
                if isinstance(elem, typ) and type_counts[typ] > 0:
                    type_counts[typ] -= 1
                    break
            else:
                return False
        return all(count == 0 for count in type_counts.values())

    def check(self, instance):
        if not isinstance(instance, set):
            return False
        return all(any(isinstance(elem, typ) for typ in self.__types__) for elem in instance)

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any
        if subclass is cls or subclass is Any or issubclass(subclass, tuple):
            return True
        if hasattr(subclass, '__bases__') and tuple in subclass.__bases__ and hasattr(subclass, '__types__') and len(subclass.__types__) == len(cls.__types__):
            return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass.__types__)
        return False

class _Tuple(type(tuple)):
    def __instancecheck__(cls, instance):
        if not isinstance(instance, tuple):
            return False
        return all(any(isinstance(x, t) for t in cls.__types__) for x in instance)

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any
        if subclass is cls or subclass is Any or issubclass(subclass, tuple):
            return True
        if hasattr(subclass, '__bases__') and tuple in subclass.__bases__ and hasattr(subclass, '__types__'):
            subclass_element_types = subclass.__types__
            return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass_element_types)
        return False

class _List(type(list)):
    def __instancecheck__(cls, instance):
        if not isinstance(instance, list):
            return False
        return all(any(isinstance(x, t) for t in cls.__types__) for x in instance)

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any
        if subclass is cls or subclass is Any or issubclass(subclass, list):
            return True
        if hasattr(subclass, '__bases__') and list in subclass.__bases__ and hasattr(subclass, '__types__'):
            subclass_element_types = subclass.__types__
            return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass_element_types)
        return False

class _Set(type(set)):
    def __instancecheck__(cls, instance):
        if not isinstance(instance, set):
            return False
        return all(any(isinstance(x, t) for t in cls.__types__) for x in instance)

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any
        if subclass is cls or subclass is Any or issubclass(subclass, set):
            return True

        if hasattr(subclass, '__bases__') and set in subclass.__bases__ and hasattr(subclass, '__types__'):
            subclass_element_types = subclass.__types__
            return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass_element_types)

        return False

class _Dict(type(dict)):
    def __new__(cls, name, bases, dct, types, key_type):
        dct['__types__'] = types
        dct['__key_type__'] = key_type
        return super().__new__(cls, name, bases, dct)

    def __instancecheck__(cls, instance):
        if not isinstance(instance, dict):
            return False

        class ValueUnionMeta(type):
            def __instancecheck__(self, inst):
                for t in self.__types__:
                    if isinstance(t, type) and hasattr(t, '__instancecheck__'):
                        result = t.__instancecheck__(inst)
                        if result:
                            return True
                    else:
                        result = isinstance(inst, t)
                        if result:
                            return True
                return False

        ValueUnion = ValueUnionMeta("DictValueUnion", (), {'__types__': cls.__types__})

        if not all(isinstance(v, ValueUnion) for v in instance.values()):
            return False
        if cls.__key_type__ is not None:
            if not all(isinstance(k, cls.__key_type__) for k in instance.keys()):
                return False
        return True

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any
        if subclass is cls or subclass is Any or issubclass(subclass, dict):
            return True
        if hasattr(subclass, '__bases__') and dict in subclass.__bases__ and hasattr(subclass, '__types__'):
            subclass_value_union_types = subclass.__types__
            keys_match = True
            if hasattr(subclass, '__key_type__') and cls.__key_type__ is not None:
                keys_match = issubclass(getattr(subclass, '__key_type__'), cls.__key_type__)
            return (
                all(any(issubclass(svt, vt) for vt in cls.__types__) for svt in subclass_value_union_types)
                and keys_match
            )
        return False

class _Any(type):
    def __instancecheck__(cls, instance):
        return True
    def __subclasscheck__(cls, subclass):
        return True

class _Pattern(type):
    def __instancecheck__(cls, x):
        if not isinstance(x, str):
            return False
        try:
            re.compile(x)
            return True
        except re.error:
            return False
    def __subclasscheck__(cls, sub):
        return issubclass(sub, str)
    def __repr__(cls):
        return "Pattern(str): a string valid as Python regex"
