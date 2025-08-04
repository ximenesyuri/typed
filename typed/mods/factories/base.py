import re
from typing import Type, Tuple as Tuple_, Union as Union_, Hashable, Callable as Callable_
from typed.mods.helper.helper import _flat, _is_null_of_type, _get_null_object, _get_type_display_name
from typed.mods.types.func import TypedFuncType

def Union(*args: Union_[Tuple_[Type], Tuple_[TypedFuncType]]) -> Union_[Type, TypedFuncType]:
    """
    Build the 'union' of types:
        > an object 'p' of 'Union(X, Y, ...)'
        > is an object of some of 'X, Y, ...'
    Can be applied to typed functions:
        > 'Union(f, g, ...): Union(f.domain, g.domain) -> Union(f.codomain, g.codomain)'
    """
    from typed.mods.types.func import TypedFuncType
    from typed.mods.helper.helper import _flat, _get_type_display_name

    if args and all((not isinstance(f, type)) and isinstance(f, TypedFuncType) for f in args):
        functors = args
        domains = [f.domain for f in functors]
        codomains = [f.codomain for f in functors]
        dom_types = [d[0] if len(d) == 1 else d for d in domains]
        if any(not (isinstance(f, TypedFuncType) and not isinstance(f, type)) for f in functors):
            raise TypeError("All functor arguments to Union must be TypedFuncType instances (not types)")

        def union_dispatcher(x):
            matching = []
            for f, dom in zip(functors, dom_types):
                if isinstance(x, dom):
                    matching.append(f)
            if not matching:
                allowed = ", ".join(_get_type_display_name(t) for t in dom_types)
                raise TypeError(
                    f"No available functor matches input {x!r}. Must be instance of one of {allowed}."
                )
            first_f = matching[0]
            if len(first_f.domain) == 1:
                first_val = first_f(x)
            else:
                first_val = first_f(*x)

            for f in matching[1:]:
                if len(f.domain) == 1:
                    fv = f(x)
                else:
                    fv = f(*x)
                if fv != first_val:
                    raise ValueError(
                        f"Ambiguous value for {[ff.__name__ for ff in matching]}:"
                        f"\n ==> argument '{x!r}'"
                        f"\n     [{matching[0].__name__} value]: '{first_val!r}'"
                        f"\n     [{f.__name__} value]: '{fv!r}'"
                    )
            return first_val

        union_dispatcher.__name__ = "Union(" + ", ".join(f.__name__ for f in functors) + ")"
        union_dispatcher.__annotations__ = {
            "x": tuple(dom_types),
            "return": tuple(codomains)
        }
        return TypedFuncType(union_dispatcher)

    elif args and all(isinstance(f, type) for f in args):
        _flattypes, _ = _flat(*args)
        if not _flattypes:
            class _EmptyUnion(type):
                def __instancecheck__(cls, instance): return False
                def __subclasscheck__(cls, subclass):
                    from typed.mods.types.base import Any
                    if subclass is cls or subclass is Any: return True
                    return False
            return _EmptyUnion("Union()", (), {})
        class _Union(type):
            def __instancecheck__(cls, instance):
                return any(isinstance(instance, t) for t in cls.__types__)
            def __subclasscheck__(cls, subclass):
                from typed.mods.types.base import Any
                if hasattr(subclass, '__types__') and getattr(cls, '__types__', None) == getattr(subclass, '__types__', None):
                    return True
                if subclass is cls or subclass is Any or subclass in cls.__types__:
                    return True
                return any(issubclass(subclass, t) for t in cls.__types__)
        class_name = f"Union({', '.join(t.__name__ for t in _flattypes)})"
        return _Union(class_name, (), {'__types__': _flattypes})

    else:
        types_seen = [type(f) for f in args]
        raise TypeError(
            f"Union arguments must all be (1) TypedFuncType instances or (2) types (classes/constructed types), "
            f"but received: {types_seen}"
        )

def Prod(*args: Union_[Tuple_[Type, int], Tuple_[TypedFuncType]]) -> Union_[Type, TypedFuncType]:
    """
    Build the 'product' of types:
        > the objects of 'Product(X, Y, ...)'
        > are the tuples '(x, y, ...)' such that
            1. 'len(x, y, ...) == len(X, Y, ...)'
            2. 'x is in X', 'y is in Y', ...
    Integer case:
        > Prod(X, n) = Prod(X, X, ...).
    Can be applied to typed functions:
        > 'Prod(f, g, ...): Prod(f.domain, g.domain, ...) -> Prod(f.codomain, g.codomain, ...)'
    """

    if args and all((not isinstance(f, type)) and isinstance(f, TypedFuncType) for f in args):
        in_types = [Prod(*f.domain) if len(f.domain) > 1 else f.domain[0] for f in args]
        out_types = [f.codomain for f in args]
        domain_type = Prod(*in_types)
        codomain_type = Prod(*out_types)
        def prod_mapper(*xs):
            if len(xs) == 1 and isinstance(xs[0], tuple):
                xs = xs[0]
            outs = []
            for f, x in zip(args, xs):
                if len(f.domain) > 1:
                    outs.append(f(*x))
                else:
                    outs.append(f(x))
            return codomain_type(*outs)
        prod_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
        prod_mapper._composed_domain_hint = (domain_type,)
        prod_mapper._composed_codomain_hint = codomain_type
        prod_mapper.__name__ = "Prod(" + ", ".join(f.__name__ for f in args) + ")"
        return TypedFuncType(prod_mapper)

    elif len(args) == 2 and isinstance(args[0], type) and isinstance(args[1], int) and args[1] > 0:
        _flattypes = (args[0],) * args[1]
        is_flexible = False
    else:
        _flattypes, is_flexible = _flat(*args)

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

    def prod_new(cls, *args):
        if len(args) == 1 and isinstance(args[0], tuple):
            return tuple.__new__(cls, args[0])
        else:
            return tuple.__new__(cls, args)

    class_name = f"Prod({', '.join(t.__name__ for t in _flattypes)})"
    return _Prod(class_name, (tuple,), {'__types__': _flattypes, '__new__': prod_new})

def UProd(*args: Union_[Tuple_[Type], TypedFuncType]) -> Union_[Type, TypedFuncType]:
    """
    Build the 'unordered product' of types:
        > the objects of 'UProd(X, Y, ...)'
        > are the tuples '(x, y, ...)' such that:
            1. 'len(x, y, ...) == len(X, Y, ...)'
            2. 'x, y, ... are in Union(X, Y, ...)'
    Can be applied to typed functions:
        > 'UProd(f, g, ...): UProd(f.domain, g.domain, ...) -> UProd(f.codomain, g.codomain, ...)'
    """
    if args and all(isinstance(f, TypedFuncType) for f in args):
        dom_types = [Prod(*f.domain) if len(f.domain) > 1 else f.domain[0] for f in args]
        cod_types = [f.codomain for f in args]
        domain_type = UProd(*dom_types)
        codomain_type = UProd(*cod_types)

        def uprod_mapper(*xs):
            if len(xs) == 1 and isinstance(xs[0], tuple):
                xs = xs[0]
            outs = []
            for f, x in zip(args, xs):
                if len(f.domain) > 1:
                    outs.append(f(*x))
                else:
                    outs.append(f(x))
            return codomain_type(*outs)

        uprod_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
        uprod_mapper._composed_domain_hint = (domain_type,)
        uprod_mapper._composed_codomain_hint = codomain_type
        uprod_mapper.__name__ = "UProd(" + ", ".join(f.__name__ for f in args) + ")"
        return TypedFuncType(uprod_mapper)
    _flattypes, is_flexible = _flat(*args)

    class _Uprod(type):
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
    class_name = f"UProd({', '.join(t.__name__ for t in _flattypes)})"
    return _Uprod(class_name, (tuple,), {'__types__': _flattypes})

def Tuple(*args: Union_[Tuple_[Type], TypedFuncType]) -> Union_[Type, TypedFuncType]:
    """
    Build the 'tuple' of types with flexible length:
        > the objects of 'Tuple(X, Y, ...)'
        > are the tuples '(x, y, ...)' such that:
            1. 'x, y, ... are in Union(X, Y, ...)'
           and
            2. The tuple can have any length >= 0.
    Can be applied to typed functions:
        > 'Tuple(f): Tuple(f.domain) -> Tuple(f.codomain)'
    """
    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], type):
        f = args[0]
        if isinstance(f, TypedFuncType):
            domain_type = Tuple(*f.domain)
            codomain_type = Tuple(f.codomain)

            def tuple_mapper(xs: domain_type) -> codomain_type:
                return codomain_type(*(f(x) for x in xs))

            tuple_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
            tuple_mapper._composed_domain_hint = (domain_type,)
            tuple_mapper._composed_codomain_hint = codomain_type
            return TypedFuncType(tuple_mapper)
        raise TypeError(f"'{getattr(f,'__name__',str(f))}' is not a typed function.")

    _flattypes, is_flexible = _flat(*args)

    if not is_flexible and args:
        raise ValueError("Tuple() based on this definition is always flexible; check _flat implementation.")

    if not _flattypes:
        class _EmptyFlexibleTupleMeta(type(tuple)):
            def __instancecheck__(cls, instance):
                return isinstance(instance, tuple)
            def __subclasscheck__(cls, subclass):
                from typed.mods.types.base import Any
                if subclass is cls or subclass is Any or issubclass(subclass, tuple):
                    return True
                return False
        return _EmptyFlexibleTupleMeta("Tuple()", (tuple,), {})

    class _ElementUnionMeta(type):
        def __instancecheck__(cls, instance):
            return isinstance(instance, tuple(cls.__types__))

    ElementUnion = _ElementUnionMeta("ElementUnion", (), {'__types__': _flattypes})

    class _Tuple(type(tuple)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, tuple):
                return False
            return all(isinstance(x, ElementUnion) for x in instance)

        def __subclasscheck__(cls, subclass):
            from typed.mods.types.base import Any
            if subclass is cls or subclass is Any or issubclass(subclass, tuple):
                return True
            if hasattr(subclass, '__bases__') and tuple in subclass.__bases__ and hasattr(subclass, '__types__'):
                subclass_element_types = subclass.__types__
                return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass_element_types)
            return False

    class_name = f"Tuple({', '.join(t.__name__ for t in _flattypes)})"
    if _flattypes:
        class_name = f"Tuple({', '.join(t.__name__ for t in _flattypes)}, ...)"
    else:
        class_name = "Tuple()"
    return _Tuple(class_name, (tuple,), {'__types__': _flattypes})

def List(*args: Union_[Tuple_[Type], TypedFuncType]) -> Union_[Type, TypedFuncType]:
    """
    Build the 'list' of types:
        > the objects of 'List(X, Y, ...)'
        > are the lists '[x, y, ...]' such that:
            1. 'x, y, ... are in Union(X, Y, ...)'
           and
            2. The list can have any length >= 0.
    Can be applied to typed functions:
        > 'List(f): List(f.domain) -> List(f.codomain)'
    """
    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], type):
        f = args[0]
        if isinstance(f, TypedFuncType):
            domain_type = List(*f.domain)
            codomain_type = List(f.codomain)
            def list_mapper(xs: domain_type) -> codomain_type:
                return codomain_type(*(f(x) for x in xs))
            list_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
            list_mapper._composed_domain_hint = (domain_type,)
            list_mapper._composed_codomain_hint = codomain_type
            return TypedFuncType(list_mapper) 
        raise TypeError(f"'{f.__name}' is not a typed function.")

    _flattypes, is_flexible = _flat(*args)

    if not is_flexible and args:
        raise ValueError("List() based on this definition is always flexible; check _flat implementation.")

    class _ElementUnionMeta(type):
        def __instancecheck__(cls, instance):
            return isinstance(instance, tuple(cls.__types__))

    ElementUnion = _ElementUnionMeta("ListElementUnion", (), {'__types__': _flattypes})

    class _List(type(list)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, list):
                return False
            return all(isinstance(x, ElementUnion) for x in instance)
        def __subclasscheck__(cls, subclass):
            from typed.mods.types.base import Any
            if subclass is cls or subclass is Any or issubclass(subclass, list):
                return True
            if hasattr(subclass, '__bases__') and list in subclass.__bases__ and hasattr(subclass, '__types__'):
                subclass_element_types = subclass.__types__
                return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass_element_types)
            return False

    class_name = f"List({', '.join(t.__name__ for t in _flattypes)})"
    if _flattypes:
        class_name = f"List({', '.join(t.__name__ for t in _flattypes)}, ...)"
    else:
        class_name = "List()"
    return _List(class_name, (list,), {'__types__': _flattypes})

def Set(*args: Union_[Tuple_[Type], TypedFuncType]) -> Union_[Type, TypedFuncType]:
    """
    Build the 'set' of types:
        > the objects of 'Set(X, Y, ...)'
        > are the sets '{x, y, ...}' such that:
            1. 'x, y, ... are in Union(X, Y, ...)'
           and
            2. The set can have any size >= 0.
            3. Elements must be hashable.
    Can be applied to typed functions:
        > 'Set(f): Set(f.domain) -> Set(f.codomain)'
    """
    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], type):
        f = args[0]
        if isinstance(f, TypedFuncType):
            domain_type = Set(*f.domain)
            codomain_type = Set(f.codomain)
            def set_mapper(xs: domain_type) -> codomain_type:
                return codomain_type(*(f(x) for x in xs))
            set_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
            set_mapper._composed_domain_hint = (domain_type,)
            set_mapper._composed_codomain_hint = codomain_type
            return TypedFuncType(set_mapper)
        raise TypeError(f"'{getattr(f,'__name__',str(f))}' is not a typed function.")

    _flattypes, is_flexible = _flat(*args)

    if not is_flexible and args:
        raise ValueError("Set() based on this definition is always flexible; check _flat implementation.")

    class _ElementUnionMeta(type):
        def __instancecheck__(cls, instance):
            return isinstance(instance, tuple(cls.__types__)) and isinstance(instance, Hashable)

    ElementUnion = _ElementUnionMeta("SetElementUnion", (), {'__types__': _flattypes})

    class _Set(type(set)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, set):
                return False
            from typed.mods.types.base import Any
            if Any is args:
                return True
            return all(isinstance(x, ElementUnion) for x in instance)

        def __subclasscheck__(cls, subclass: Type) -> bool:
            from typed.mods.types.base import Any

            if subclass is cls or subclass is Any or issubclass(subclass, set):
                return True

            if hasattr(subclass, '__bases__') and set in subclass.__bases__ and hasattr(subclass, '__types__'):
                subclass_element_types = subclass.__types__
                return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass_element_types)

            return False

    class_name = f"Set({', '.join(t.__name__ for t in _flattypes)})"
    if _flattypes:
        class_name = f"Set({', '.join(t.__name__ for t in _flattypes)}, ...)"
    else:
        class_name = "Set()"

    return _Set(class_name, (set,), {'__types__': _flattypes})

def Dict(*args: Union_[Tuple_[Type], TypedFuncType], keys=None) -> Union_[Type, TypedFuncType]:
    """
    Build the 'dict' of types:
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
    if not args:
        class _AnyAnyDictMeta(type(dict)):
            def __instancecheck__(cls, instance):
                return isinstance(instance, dict)
            def __subclasscheck__(cls, subclass):
                from typed.mods.types.base import Any
                if subclass is cls or subclass is Any or issubclass(subclass, dict):
                    return True
                return False
        return _AnyAnyDictMeta("Dict()", (dict,), {})

    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], type):
        f = args[0]
        if isinstance(f, TypedFuncType):
            domain_type = Dict(f.domain, keys=keys)
            codomain_type = Dict(f.codomain, keys=keys)
            def dict_mapper(d: domain_type) -> codomain_type:
                return codomain_type({k: f(v) for k, v in d.items()})
            dict_mapper.__annotations__ = {'d': domain_type, 'return': codomain_type}
            dict_mapper._composed_domain_hint = (domain_type,)
            dict_mapper._composed_codomain_hint = codomain_type
            return TypedFuncType(dict_mapper)

    _flattypes, is_flexible = _flat(*args)

    if not is_flexible and args:
        pass

    class _ValueUnionMeta(type):
        def __instancecheck__(cls, instance):
            for t in cls.__types__:
                if isinstance(t, type) and hasattr(t, '__instancecheck__'):
                    result = t.__instancecheck__(instance)
                    if result:
                        return True
                else:
                    result = isinstance(instance, t)
                    if result:
                        return True
            return False
    ValueUnion = _ValueUnionMeta("DictValueUnion", (), {'__types__': _flattypes})

    key_type = keys
    if key_type is not None:
        if not isinstance(key_type, type):
            raise TypeError(f"keys= must be a type, got {key_type!r}")
        if not issubclass(key_type, str):
            raise TypeError("keys= must be subclass of str")
    else:
        key_type = None

    class _Dict(type(dict)):
        __types__ = _flattypes
        __key_type__ = key_type

        def __instancecheck__(cls, instance):
            if not isinstance(instance, dict):
                return False
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

    typename = f"Dict({', '.join(t.__name__ for t in _flattypes)})"
    if key_type is not None:
        typename = f"Dict({', '.join(t.__name__ for t in _flattypes)}, keys={key_type.__name__})"
    return _Dict(typename, (dict,), {'__types__': _flattypes, '__key_type__': key_type})

def Null(typ: Union_[Type, Callable_]) -> Type:
    """
    Null(T) returns a class that's a subclass of T (if possible).
    isinstance(x, Null(T)) is True iff x is the null/empty of T.
    """
    from typed.mods.types.base import Any
    if typ is Any:
        class _NullAny(type):
            def __instancecheck__(cls, instance):
                for t in (str, int, float, bool, type(None), list, tuple, set, dict):
                    if _is_null_of_type(instance, t):
                        return True
                for Fact in [List, Tuple, Set, Dict]:
                    for Tp in (str, int, float, bool):
                        try:
                            if _is_null_of_type(instance, Fact(Tp)):
                                return True
                        except Exception:
                            pass
                try:
                    if _is_null_of_type(instance, List(Dict(str))):
                        return True
                    if _is_null_of_type(instance, List(List(str))):
                        return True
                except Exception:
                    pass
                return False
            def __repr__(cls):
                return "Null[Any]"
        return _NullAny("Null[Any]", (object,), {})

    null_obj = _get_null_object(typ)

    class _Null(type):
        null = null_obj
        def __instancecheck__(cls, instance):
            return instance == null_obj
        def __repr__(cls):
            return f"<Null[{getattr(typ, '__name__', str(typ))}]>"
    class_name = f"Null[{getattr(typ, '__name__', str(typ))}]"
    return _Null(class_name, (), {})
