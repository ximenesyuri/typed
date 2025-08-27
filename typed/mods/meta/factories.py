from typed.mods.helper.helper import _inner_union, _inner_dict_union

class TUPLE(type(tuple)):
    """
    Build the typed 'flexible length tuple' factory type:
        > the objects of 'Tuple' are tuples
        > the objects of 'Tuple(X, Y, ...)'
        > are the tuples '(x, y, ...)' such that:
            1. 'x, y, ... are in Union(X, Y, ...)'
           and
            2. The tuple can have any length >= 0.
    Can be applied to typed functions:
        > 'Tuple(f): Tuple(f.domain) -> Tuple(f.codomain)'
    """
    def __instancecheck__(cls, instance):
        if not isinstance(instance, tuple):
            return False
        return all(isinstance(x, _inner_union(*types)) for x in instance)

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any
        if subclass is cls or subclass is Any or issubclass(subclass, tuple):
            return True
        if hasattr(subclass, '__bases__') and tuple in subclass.__bases__ and hasattr(subclass, '__types__'):
            subclass_element_types = subclass.__types__
            return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass_element_types)
        return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.factories.types import _Tuple_
        return _Tuple_(*args, **kwargs)

    @staticmethod
    def __convert__(obj):
        if isinstance(obj, tuple):
            return tuple(obj)
        if hasattr(obj, "__iter__") or hasattr(obj, "__getitem__"):
            try: return tuple(obj)
            except Exception: pass
        raise TypeError(f"Cannot convert {obj!r} to Tuple.")

class LIST(type(list)):
    """
    Build the typed 'list' factory type:
        > the objects of 'List' are lists
        > the objects of 'List(X, Y, ...)'
        > are the lists '[x, y, ...]' such that:
            1. 'x, y, ... are in Union(X, Y, ...)'
           and
            2. The list can have any length >= 0.
    Can be applied to typed functions:
        > 'List(f): List(f.domain) -> List(f.codomain)'
    """
    def __instancecheck__(cls, instance):
        if not isinstance(instance, list):
            return False
        return all(isinstance(x, _inner_union(*types)) for x in instance)

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any
        if subclass is cls or subclass is Any or issubclass(subclass, list):
            return True
        if hasattr(subclass, '__bases__') and list in subclass.__bases__ and hasattr(subclass, '__types__'):
            subclass_element_types = subclass.__types__
            return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass_element_types)
        return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.factories.types import _List_
        return _List_(*args, **kwargs)

    @staticmethod
    def __convert__(obj):
        if isinstance(obj, list):
            return list(obj)
        if hasattr(obj, "__iter__") or hasattr(obj, "__getitem__"):
            try: return list(obj)
            except Exception: pass
        raise TypeError(f"Cannot convert {obj!r} to List.")

class SET(type(set)):
    """
    The typed 'set' of factory type:
        > the objects of Set are sets
        > the objects of 'Set(X, Y, ...)'
        > are the sets '{x, y, ...}' such that:
            1. 'x, y, ... are in Union(X, Y, ...)'
           and
            2. The set can have any size >= 0.
            3. Elements must be hashable.
    Can be applied to typed functions:
        > 'Set(f): Set(f.domain) -> Set(f.codomain)'
    """
    def __instancecheck__(cls, instance):
        if not isinstance(instance, set):
            return False
        from typed.mods.types.base import Any
        if Any is args:
            return True
        return all(isinstance(x, _inner_union(types)) for x in instance)

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any
        if subclass is cls or subclass is Any or issubclass(subclass, set):
            return True
        if hasattr(subclass, '__bases__') and set in subclass.__bases__ and hasattr(subclass, '__types__'):
            subclass_element_types = subclass.__types__
            return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass_element_types)
        return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.factories.types import _Set_
        return _Set_(*args, **kwargs)

    @staticmethod
    def __convert__(obj):
        if isinstance(obj, set):
            return set(obj)
        if hasattr(obj, "__iter__"):
            try: return set(obj)
            except Exception: pass
        raise TypeError(f"Cannot convert {obj!r} to Set.")

class DICT(type(dict)):
    """
    The typed dictionary factory type:
        > the objects of 'Dict' are dictionaries
        > the objects of 'Dict(X, Y, ...)'
        > are the dictionaries '{k: v, ...}' such that:
            1. 'v, ... are in Union(X, Y, ...)' (keys are not restricted)
           and
            2. The dict can have any size >= 0.
            3. Keys must be hashable (standard dict behavior).
    Accept argument 'keys':
        > the objects of 'Dict(X, Y, ..., keys=K)'
        > are the objects 'd' of 'Dict(X, Y, ...)' such that:
            1. 'issubclass(K, Str) is True'
            2. 'isinstance(key, K) is True' for every 'k in d.keys()'
    Can be applied to typed functions:
        > 'Dict(f): Dict(f.domain) -> Dict(f.codomain)' such that
            1. 'f({k: v}) = {k: f(v)}'
    """
    def __instancecheck__(cls, instance):
        if not isinstance(instance, dict):
            return False
        if not all(isinstance(v, _inner_dict_union(cls.__types__)) for v in instance.values()):
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

    def __call__(cls, *args, **kwargs):
        from typed.mods.factories.types import _Dict_
        return _Dict_(*args, **kwargs)

    @staticmethod
    def __convert__(obj):
        if isinstance(obj, dict):
            return dict(obj)
        if hasattr(obj, "__iter__"):
            try: return dict(obj)
            except Exception: pass
        if hasattr(obj, "__dict__"):
            return dict(obj.__dict__)
        raise TypeError(f"Cannot convert {obj!r} to Dict.")
