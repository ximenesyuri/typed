import re
from typed.mods.helper.helper import _inner_union, _inner_dict_union, _name

class __UNIVERSE__(type):
    def __new__(mcls, name, bases, namespace, **kwds):
        if '__instancecheck__' not in namespace:
            raise TypeError(f"{name} must implement __instancecheck__")

        if '__subclasscheck__' not in namespace:
            namespace['__subclasscheck__'] = type.__subclasscheck__

        def __contains__(cls, obj):
            return isinstance(obj, cls)
        namespace['__contains__'] = __contains__
        return super().__new__(mcls, name, bases, namespace, **kwds)

class _TYPE_(type, metaclass=__UNIVERSE__):
    def __instancecheck__(cls, instance):
        return isinstance(instance, type)

    def __eq__(cls, other):
        return issubclass(cls, other) and issubclass(other, cls)

    def __ne__(cls, other):
        return not (issubclass(cls, other) or issubclass(other, cls))

    def __lt__(cls, other):
        return issubclass(cls, other) and not issubclass(other, cls)

    def __le__(cls, other):
        return issubclass(cls, other)

    def __gt__(cls, other):
        return issubclass(other, cls) and not issubclass(cls, other)

    def __ge__(cls, other):
        return issubclass(other, cls)

    def __hash__(cls):
        return id(cls)

    def __call__(cls, *args, **kwargs):
        if args and isinstance(args[0], str):
            return type.__call__(cls, *args, **kwargs)
        if len(args) != 1:
            raise TypeError(
                f"{cls.__name__} expected 1 argument (object to type-convert), "
                f"got {len(args)}"
            )

        obj = args[0]
        from typed.mods.types.base import (
            Str, Int, Float, Bool, Nill, Any,
            List, Tuple, Set, Dict
        )
        types_map = {
            type(None): Nill,
            bool: Bool,
            int: Int,
            float: Float,
            str: Str,
            list: List(Any),
            tuple: Tuple(Any),
            dict: Dict(Any),
            set: Set(Any)
        }
        for k, v in types_map.items():
            if type(obj) is k:
                return v
        return type(obj)

class _META_(_TYPE_):
    def __instancecheck__(cls, instance):
        return isinstance(instance, type) and issubclass(instance, type)

    def __subclasscheck__(cls, subclass):
        return (
                isinstance(subclass, type)
                and issubclass(instance, type)
                and issubclass(subclass, cls)
            )

class _DISCOURSE_(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.types.attr import ATTR
        from typed.mods.types.func import Generator
        return (
            isinstance(type(instance), ATTR("__iter__"))
            and isinstance(type(instance).__iter__, Generator)
        )

class NILL(_TYPE_):
    def __instancecheck__(cls, instance):
        return False
    def __subclasscheck__(cls, subclass):
        return False

class INT(_TYPE_):
    def __instancecheck__(cls, instance):
        return isinstance(instance, int)

    def __convert__(cls, obj):
        from typed.mods.types.base import TYPE
        from typed.mods.types.attr import ATTR
        from typed.mods.helper.helper import _name
        if isinstance(TYPE(obj), ATTR('__int__')):
            return int(obj)
        raise TypeError(
            "Wrong type in Int function.\n"
            f" ==> '{obj}': has an unexpected type."
            f"     [expected_type] an instance of {_name(ATTR('__int__'))}"
            f"     [received_type] {_name(TYPE(obj))}"
        )

class FLOAT(_TYPE_):
    def __instancecheck__(cls, instance):
        return isinstance(instance, float)

    def __convert__(cls, obj):
        from typed.mods.types.base import TYPE
        from typed.mods.types.attr import ATTR
        from typed.mods.helper.helper import _name
        if isinstance(TYPE(obj), ATTR('__float__')):
            return float(obj)
        raise TypeError(
            "Wrong type in Float function.\n"
            f" ==> '{obj}': has an unexpected type."
            f"     [expected_type] an instance of {_name(ATTR('__int__'))}"
            f"     [received_type] {_name(TYPE(obj))}"
        )

class STR(_TYPE_):
    def __instancecheck__(cls, instance):
        return isinstance(instance, str)

class BOOL(_TYPE_):
    def __instancecheck__(cls, instance):
        return isinstance(instance, bool)

class ANY(_TYPE_):
    def __instancecheck__(cls, instance):
        return True

    def __subclasscheck__(cls, subclass):
        return True

class PATTERN(STR):
    def __instancecheck__(cls, instance):
        if not isinstance(instance, str):
            return False
        try:
            re.compile(instance)
            return True
        except re.error:
            return False

    def __subclasscheck__(cls, subclass):
        return issubclass(subclass, cls)

class TUPLE(_TYPE_):
    """
    Build the typed 'Tuple' parametric type:
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
        from typed.mods.parametric.base import _Tuple_
        return _Tuple_(*args, **kwargs)

    @staticmethod
    def __convert__(obj):
        if isinstance(obj, tuple):
            return tuple(obj)
        if hasattr(obj, "__iter__") or hasattr(obj, "__getitem__"):
            try: return tuple(obj)
            except Exception: pass
        raise TypeError(f"Cannot convert {obj!r} to Tuple.")

class LIST(_TYPE_):
    """
    Build the typed 'List' parametric type:
        > the objects of 'List' are lists
        > the objects of 'List(X, Y, ...)'
        > are the lists '[x, y, ...]' such that:
            1. 'x, y, ... are in Union(X, Y, ...)' and
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
        from typed.mods.parametric.base import _List_
        return _List_(*args, **kwargs)

    @staticmethod
    def __convert__(obj):
        if isinstance(obj, list):
            return list(obj)
        if hasattr(obj, "__iter__") or hasattr(obj, "__getitem__"):
            try: return list(obj)
            except Exception: pass
        raise TypeError(f"Cannot convert {obj!r} to List.")

class SET(_TYPE_):
    """
    The typed 'Set' of parametric type:
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
        from typed.mods.parametric.base import _Set_
        return _Set_(*args, **kwargs)

    @staticmethod
    def __convert__(obj):
        if isinstance(obj, set):
            return set(obj)
        if hasattr(obj, "__iter__"):
            try: return set(obj)
            except Exception: pass
        raise TypeError(f"Cannot convert {obj!r} to Set.")

class DICT(_TYPE_):
    """
    The typed 'Dict' parametric type:
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
        from typed.mods.parametric.base import _Dict_
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
