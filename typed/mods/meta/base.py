from typed.mods.helper.helper import (
    _inner_union,
    _inner_dict_union,
    _from_typing,
    _issubtype,
    _isweaksubtype
)

class __UNIVERSE__(type):
    def __new__(mcls, name, bases, namespace, **kwds):
        if '__instancecheck__' not in namespace:
            raise TypeError(f"{name} must implement __instancecheck__")

        if '__subclasscheck__' not in namespace:
            namespace['__subclasscheck__'] = type.__subclasscheck__

        def __contains__(cls, obj):
            return isinstance(obj, cls)
        namespace['__contains__'] = __contains__
        return type.__new__(mcls, name, bases, namespace, **kwds)

    def __eq__(cls, other):
        return _TYPE_.__eq__(cls, other)
    def __ne__(cls, other):
        return _TYPE_.__ne__(cls, other)
    def __le__(cls, other):
        return _TYPE_.__le__(cls, other)
    def __lt__(cls, other):
        return _TYPE_.__lt__(cls, other)
    def __ge__(cls, other):
        return _TYPE_.__ge__(cls, other)
    def __gt__(cls, other):
        return _TYPE_.__gt__(cls, other)
    def __lshift__(cls, other):
        return _TYPE_.__lshift__(cls, other)
    def __rshift__(cls, other):
        return _TYPE_.__rshift__(cls, other)
    def __hash__(cls):
        return _TYPE_.__hash__(cls)

class _TYPE_(type, metaclass=__UNIVERSE__):
    def __instancecheck__(cls, instance):
        if _from_typing(type(instance)) or _from_typing(instance):
            return False
        return _issubtype(type(instance), _TYPE_)

    def __invert__(cls):
        cls.__tilde__=True
        return cls

    def __eq__(cls, other):
        if _from_typing(cls) or _from_typing(other):
            return False
        try:
            if hasattr(other, "__tilde__"):
                if other.__tilde__:
                    return _isweaksubtype(cls, other) and _isweaksubtype(other, cls)
            return _issubtype(cls, other) and _issubtype(other, cls)
        except:
            return False

    def __ne__(cls, other):
        if _from_typing(cls) or _from_typing(other):
            return True
        try:
            return not (_issubtype(cls, other) or _issubtype(other, cls))
        except:
            return True

    def __lt__(cls, other):
        if _from_typing(cls) or _from_typing(other):
            return False
        try:
            return _issubtype(cls, other) and not _issubtype(other, cls)
        except:
            return False

    def __le__(cls, other):
        if _from_typing(cls) or _from_typing(other):
            return False
        try:
            return _issubtype(cls, other)
        except:
            return False

    def __gt__(cls, other):
        if _from_typing(cls) or _from_typing(other):
            return False
        try:
            return _issubtype(other, cls) and not _issubtype(cls, other)
        except:
            return False

    def __ge__(cls, other):
        if _from_typing(cls) or _from_typing(other):
            return False
        try:
            return _issubtype(other, cls)
        except:
            return False

    def __lshift__(cls, other):
        if _from_typing(cls) or _from_typing(other):
            return False
        try:
            return _isweaksubtype(cls, other)
        except:
            return False

    def __rshift__(cls, other):
        if _from_typing(cls) or _from_typing(other):
            return False
        try:
            return _isweaksubtype(other, cls)
        except:
            return False

    def __hash__(cls):
        return id(cls)

    def __subclasscheck__(cls, subclass):
        if _from_typing(cls) or _from_typing(subclass):
            return False
        try:
            return _issubtype(cls, subclass)
        except TypeError:
            return False

    def __call__(cls, *args, **kwargs):
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

class _ABSTRACT_(_TYPE_):
    def __instancecheck__(cls, instance):
        return _issubtype(instance, _TYPE_)

class _UNIVERSAL_(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE
        return TYPE(instance) == __UNIVERSE__

class _META_(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE
        return instance in TYPE and _issubtype(instance, _TYPE_)

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import TYPE
        return (
                subclass in TYPE
                and _issubtype(subclass, TYPE)
                and _issubtype(subclass, cls)
            )

class _DISCOURSE_(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.factories.meta import ATTR
        from typed.mods.types.func import Generator
        from typed.mods.types.base import TYPE
        return (
            TYPE(instance) in ATTR("__iter__")
            and TYPE(instance).__iter__ in Generator
        )

class _PARAMETRIC_(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.factories.meta import ATTR
        from typed.mods.types.func import Factory
        from typed.mods.types.base import TYPE
        return (
            TYPE(instance) in ATTR("__call__")
            and instance.__call__ in Factory
        )

class NILL(_TYPE_):
    def __instancecheck__(cls, instance):
        return instance is None
    def __subclasscheck__(cls, subclass):
        return False

class INT(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import Int, TYPE
        return isinstance(instance, int) or _issubtype(TYPE(instance), Int)

    def __convert__(cls, obj):
        from typed.mods.types.base import TYPE
        from typed.mods.factories.meta import ATTR
        from typed.mods.helper.helper import _name
        if TYPE(obj) in ATTR('__int__'):
            return int(obj)
        raise TypeError(
            "Wrong type in Int function.\n"
            f" ==> '{obj}': has an unexpected type."
            f"     [expected_type] an instance of {_name(ATTR('__int__'))}"
            f"     [received_type] {_name(TYPE(obj))}"
        )

class FLOAT(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import Float, TYPE
        return isinstance(instance, float) or _issubtype(TYPE(instance), Float)

    def __convert__(cls, obj):
        from typed.mods.types.base import TYPE
        from typed.mods.factories.meta import ATTR
        from typed.mods.helper.helper import _name
        if TYPE(obj) in ATTR('__float__'):
            return float(obj)
        raise TypeError(
            "Wrong type in Float function.\n"
            f" ==> '{_name(obj)}': has an unexpected type."
            f"     [expected_type] an instance of {_name(ATTR('__int__'))}"
            f"     [received_type] {_name(TYPE(obj))}"
        )

class STR(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import Str, TYPE
        return isinstance(instance, str) or _issubtype(TYPE(instance), Str)

class BOOL(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import Bool, TYPE
        return isinstance(instance, bool) or _issubtype(TYPE(instance), Bool)

class BYTES(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import Bytes, TYPE
        return isinstance(instance, bytes) or _issubtype(TYPE(instance), Bytes)

class ANY(_TYPE_):
    def __instancecheck__(cls, instance):
        return True

    def __subclasscheck__(cls, subclass):
        return True

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
        from typed.mods.types.base import Tuple, TYPE
        if not isinstance(instance, tuple) and not _issubtype(TYPE(instance), Tuple):
            return False
        if hasattr(cls, '__types__'):
            return all(isinstance(x, _inner_union(cls.__types__)) for x in instance)
        return True

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any, Tuple
        if subclass is cls or subclass is Any or _issubtype(subclass, Tuple):
            return True
        if hasattr(subclass, '__bases__') and (Tuple in subclass.__bases__) and hasattr(subclass, '__types__'):
            subclass_element_types = subclass.__types__
            return all(any(_issubtype(st, ct) for ct in cls.__types__) for st in subclass_element_types)
        return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.parametric.base import _Tuple_
        return _Tuple_(*args, **kwargs)

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
        from typed.mods.types.base import List, TYPE
        if not isinstance(instance, list) and not _issubtype(TYPE(instance), List):
            return False
        if hasattr(cls, '__types__'):
            return all(isinstance(x, cls.__types__) for x in instance)
        return True

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any, List
        if subclass is cls or subclass is Any or _issubtype(subclass, List):
            return True
        if hasattr(subclass, '__bases__') and List in subclass.__bases__ and hasattr(subclass, '__types__'):
            subclass_element_types = subclass.__types__
            return all(any(_issubtype(st, ct) for ct in cls.__types__) for st in subclass_element_types)
        return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.parametric.base import _List_
        return _List_(*args, **kwargs)

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
        from typed.mods.types.base import Set, TYPE
        if not isinstance(instance, set) and not _issubtype(TYPE(instance), Set):
            return False
        from typed.mods.types.base import Any
        if Any is cls.__bases__:
            return True
        if hasattr(cls, "__types__"):
            return all(isinstance(x, _inner_union(cls.__types__)) for x in instance)
        return True

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any, Set
        if subclass is cls or subclass is Any or _issubtype(subclass, Set):
            return True
        if hasattr(subclass, '__bases__') and Set in subclass.__bases__ and hasattr(subclass, '__types__'):
            subclass_element_types = subclass.__types__
            return all(any(_issubtype(st, ct) for ct in cls.__types__) for st in subclass_element_types)
        return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.parametric.base import _Set_
        return _Set_(*args, **kwargs)

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
        from typed.mods.types.base import Dict, TYPE
        if not isinstance(instance, dict) and not _issubtype(TYPE(instance), Dict):
            return False
        if hasattr(cls, "__types__"):
            if not all(isinstance(v, _inner_dict_union(cls.__types__)) for v in instance.values()):
                return False
        if hasattr(cls, "__key_type__"):
            if cls.__key_type__ is not None:
                if not all(isinstance(k, cls.__key_type__) for k in instance.keys()):
                    return False
        return True

    def __subclasscheck__(cls, subclass):
        from typed.mods.types.base import Any, Dict
        if subclass is cls or subclass is Any or _issubtype(subclass, Dict):
            return True
        if hasattr(subclass, '__bases__') and Dict in subclass.__bases__ and hasattr(subclass, '__types__'):
            subclass_value_union_types = subclass.__types__
            keys_match = True
            if hasattr(subclass, '__key_type__') and cls.__key_type__ is not None:
                keys_match = _issubtype(getattr(subclass, '__key_type__'), cls.__key_type__)
            return (
                all(any(_issubtype(svt, vt) for vt in cls.__types__) for svt in subclass_value_union_types)
                and keys_match
            )
        return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.parametric.base import _Dict_
        return _Dict_(*args, **kwargs)

class PATTERN(STR):
    def __instancecheck__(cls, instance):
        import re
        from typed.mods.types.base import Str
        if not isinstance(instance, Str):
            return False
        try:
            re.compile(instance)
            return True
        except re.error:
            return False
