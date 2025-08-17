import re
from typing import Type, Tuple as Tuple_, Union as Union_, Hashable, Callable as Callable_
from typed.mods.types.func import Typed
from typed.mods.helper.null import  _null, _null_from_list
from typed.mods.helper.helper import (
    _name,
    _name_list,
    _inner_union,
    _inner_dict_union
)

def Union(*args: Union_[Tuple_[Type], Tuple_[Typed]]) -> Union_[Type, Typed]:
    """
    Build the 'union' of types:
        > an object 'p' of 'Union(X, Y, ...)'
        > is an object of some of 'X, Y, ...'
    Can be applied to typed functions:
        > 'Union(f, g, ...): Union(f.domain, g.domain) -> Union(f.codomain, g.codomain)'
    """
    T = (Typed, type)

    if not args:
        return type(None)
    if all((not isinstance(f, type)) and isinstance(f, Typed) for f in args):
        funcs = args
        domains = [f.domain for f in funcs]
        codomains = [f.codomain for f in funcs]
        dom_types = [d[0] if len(d) == 1 else d for d in domains]
        if any(not (isinstance(f, Typed) and not isinstance(f, type)) for f in funcs):
            raise TypeError(
                "Wrong type in Union factory: \n"
                f" ==> {_name(f)}: has unexpected type\n"
                 "     [expected_type] Typed"
                f"     [received_type] {_name(type(f))}"
            )

        def union_dispatcher(x):
            matching = []
            for f, dom in zip(funcs, dom_types):
                if isinstance(x, dom):
                    matching.append(f)
            if not matching:
                allowed = ", ".join(_name(t) for t in dom_types)
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
                        f"Ambiguous value for {[_name(ff) for ff in matching]}:"
                        f"\n ==> argument '{x!r}'"
                        f"\n     [{matching[0].__name__} value]: '{first_val!r}'"
                        f"\n     [{f.__name__} value]: '{fv!r}'"
                    )
            return first_val

        union_dispatcher.__name__ = f"Union({_name_list(*funcs)})"
        union_dispatcher.__annotations__ = {
            "x": tuple(dom_types),
            "return": tuple(codomains)
        }
        return Typed(union_dispatcher)

    elif all(isinstance(f, type) for f in args):
        types = args
    elif all(isinstance(t, T) for t in args):
        raise TypeError(
            "Mixed argument types: \n"
            " ==> Union factory cannot receive both typed functions and types as arguments."
        )
    else:
        for t in args:
            if not isinstance(t, T):
                raise TypeError(
                    "Wrong type in Union factory: \n"
                    f" ==> {_name(t)}: has unexpected type\n"
                     "     [expected_type] TYPE or Typed"
                    f"     [received_type] {_name(type(t))}"
                )

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

    class_name = f"Union({_name_list(*types)})"

    __null__ = _null_from_list(*types)

    return _Union(class_name, (), {
        '__display__': class_name,
        '__types__': types,
        '__null__': __null__
    })

def Prod(*args: Union_[Tuple_[Type, int], Tuple_[Typed]]) -> Union_[Type, Typed]:
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

    T = (Typed, type)
    if not args:
        return type(None)
    if all((not isinstance(f, type)) and isinstance(f, Typed) for f in args):
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
        prod_mapper.__name__ = f"Prod({_name_list(*args)})"
        return Typed(prod_mapper)

    elif len(args) == 2 and isinstance(args[0], type) and isinstance(args[1], int) and args[1] > 0:
        types = (args[0],) * args[1]
    elif all(isinstance(t, type) for t in args):
        types = args
    elif all(isinstance(t, T) for t in args):
        raise TypeError(
            "Mixed argument types: \n"
            " ==> 'Prod' factory cannot receive both typed functions and types as arguments."
        )
    else:
        for t in args:
            if not isinstance(t, T):
                raise TypeError(
                "Wrong type in 'Prod' factory: \n"
                f" ==> '{_name(t)}': has unexpected type\n"
                 "     [expected_type] TYPE or Typed"
                f"     [received_type] {_name(type(t))}"
            )

    class _Prod(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, tuple):
                return False
            if len(instance) != len(cls.__types__):
                return False
            return all(isinstance(x, t) for x, t in zip(instance, cls.__types__))

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

    class_name = f"Prod({_name_list(*types)})"
    return _Prod(class_name, (tuple,), {
        "__display__": class_name,
        '__types__': types,
        '__new__': prod_new,
        "__null__": tuple(_null(t) for t in types)
    })

def UProd(*args: Union_[Tuple_[Type], Typed]) -> Union_[Type, Typed]:
    """
    Build the 'unordered product' of types:
        > the objects of 'UProd(X, Y, ...)'
        > are the tuples '(x, y, ...)' such that:
            1. 'len(x, y, ...) == len(X, Y, ...)'
            2. 'x, y, ... are in Union(X, Y, ...)'
    Can be applied to typed functions:
        > 'UProd(f, g, ...): UProd(f.domain, g.domain, ...) -> UProd(f.codomain, g.codomain, ...)'
    """
    T = (Typed, type)
    if not args:
        return type(None)
    if all((not isinstance(f, type)) and isinstance(f, Typed) for f in args):
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
        uprod_mapper.__name__ = f"UProd({_name_list(*args)})"
        return Typed(uprod_mapper)

    elif all(isinstance(t, type) for t in args):
        types = args
    elif all(isinstance(t, T) for t in args):
        raise TypeError(
            "Mixed argument types: \n"
            " ==> 'Prod' factory cannot receive both typed functions and types as arguments."
        )
    else:
        for t in args:
            if not isinstance(t, T):
                raise TypeError(
                "Wrong type in 'Prod' factory: \n"
                f" ==> '{_name(t)}': has unexpected type\n"
                 "     [expected_type] TYPE or Typed"
                f"     [received_type] {_name(type(t))}"
            )

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

    class_name = f"UProd({_name_list(*types)})"
    return _Uprod(class_name, (tuple,), {
        "__display__": class_name,
        '__types__': types,
        "__null__": set(_null(t) for t in types)
    })

def Tuple(*args: Union_[Tuple_[Type], Typed]) -> Union_[Type, Typed]:
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
    if not args:
        return type(None)
    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], type):
        f = args[0]
        if isinstance(f, Typed):
            domain_type = Tuple(*f.domain)
            codomain_type = Tuple(f.codomain)

            def tuple_mapper(xs: domain_type) -> codomain_type:
                return codomain_type(*(f(x) for x in xs))

            tuple_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
            tuple_mapper._composed_domain_hint = (domain_type,)
            tuple_mapper._composed_codomain_hint = codomain_type
            return Typed(tuple_mapper)
        raise TypeError(
            "Argument with unexpected type in Tuple factory."
            f" ==> '{_name(f)}' has wrong type."
             "     [expected_type] Typed"
            f"     [received_type] {_name(type(f))}"
        )
    elif all(isinstance(f, type) for f in args):
        types = args
    elif all(isinstance(t, T) for t in args):
        raise TypeError(
            "Mixed argument types: \n"
            " ==> 'Tuple' factory cannot receive both typed functions and types as arguments."
        )
    else:
        for t in args:
            if not isinstance(t, T):
                raise TypeError(
                "Wrong type in 'Tuple' factory: \n"
                f" ==> '{_name(t)}': has unexpected type\n"
                 "     [expected_type] TYPE or Typed"
                f"     [received_type] {_name(type(t))}"
            )

    class _Tuple(type(tuple)):
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

    __null__ = _null_from_list(*types)

    class_name = f"Tuple({_name_list(*types)})"
    return _Tuple(class_name, (tuple,), {
        '__display__': class_name,
        '__types__': types,
        '__null__': tuple(__null__) if __null__ is not None else None
    })

def List(*args: Union_[Tuple_[Type], Typed]) -> Union_[Type, Typed]:
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
    if not args:
        return type(None)
    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], type):
        f = args[0]
        if isinstance(f, Typed):
            domain_type = List(*f.domain)
            codomain_type = List(f.codomain)
            def list_mapper(xs: domain_type) -> codomain_type:
                return codomain_type(*(f(x) for x in xs))
            list_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
            list_mapper._composed_domain_hint = (domain_type,)
            list_mapper._composed_codomain_hint = codomain_type
            return Typed(list_mapper)
        raise TypeError(
            "Argument with unexpected type in Tuple factory."
            f" ==> '{_name(f)}' has wrong type."
             "     [expected_type] Typed"
            f"     [received_type] {_name(type(f))}"
        )

    elif all(isinstance(f, type) for f in args):
        types = args

    elif all(isinstance(t, T) for t in args):
        raise TypeError(
            "Mixed argument types: \n"
            " ==> 'List' factory cannot receive both typed functions and types as arguments."
        )
    else:
        for t in args:
            if not isinstance(t, T):
                raise TypeError(
                "Wrong type in 'List' factory: \n"
                f" ==> '{_name(t)}': has unexpected type\n"
                 "     [expected_type] TYPE or Typed"
                f"     [received_type] {_name(type(t))}"
            )

    class _List(type(list)):
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

    __null__ = _null_from_list(*types)

    class_name = f"List({_name_list(*types)})"
    return _List(class_name, (tuple,), {
        '__display__': class_name,
        '__types__': types,
        '__null__': list(__null__) if __null__ is not None else None
    })

def Set(*args: Union_[Tuple_[Type], Typed]) -> Union_[Type, Typed]:
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
    if not args:
        return type(None)
    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], type):
        f = args[0]
        if isinstance(f, Typed):
            domain_type = Set(*f.domain)
            codomain_type = Set(f.codomain)
            def set_mapper(xs: domain_type) -> codomain_type:
                return codomain_type(*(f(x) for x in xs))
            set_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
            set_mapper._composed_domain_hint = (domain_type,)
            set_mapper._composed_codomain_hint = codomain_type
            return Typed(set_mapper)
        raise TypeError(
            "Wrong type in Union factory: \n"
            f" ==> {_name(f)}: has unexpected type\n"
             "     [expected_type] Typed"
            f"     [received_type] {_name(type(f))}"
        )

    elif all(isinstance(f, type) for f in args):
        types = args

    elif all(isinstance(t, T) for t in args):
        raise TypeError(
            "Mixed argument types: \n"
            " ==> 'Set' factory cannot receive both typed functions and types as arguments."
        )
    else:
        for t in args:
            if not isinstance(t, T):
                raise TypeError(
                "Wrong type in 'Set' factory: \n"
                f" ==> '{_name(t)}': has unexpected type\n"
                 "     [expected_type] TYPE or Typed"
                f"     [received_type] {_name(type(t))}"
            )

    class _Set(type(set)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, set):
                return False
            from typed.mods.types.base import Any
            if Any is args:
                return True
            return all(isinstance(x, _inner_union(types)) for x in instance)

        def __subclasscheck__(cls, subclass: Type) -> bool:
            from typed.mods.types.base import Any
            if subclass is cls or subclass is Any or issubclass(subclass, set):
                return True
            if hasattr(subclass, '__bases__') and set in subclass.__bases__ and hasattr(subclass, '__types__'):
                subclass_element_types = subclass.__types__
                return all(any(issubclass(st, ct) for ct in cls.__types__) for st in subclass_element_types)
            return False

    __null__ = _null_from_list(*types)

    class_name = f"Set({_name_list(*types)})"
    return _Set(class_name, (set,), {
        '__display__': class_name,
        '__types__': types,
        '__null__': set(__null__) if __null__ is not None else None
    })

def Dict(*args: Union_[Tuple_[Type], Typed], keys=str) -> Union_[Type, Typed]:
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
        return type(None)

    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], type):
        f = args[0]
        if isinstance(f, Typed):
            domain_type = Dict(f.domain, keys=keys)
            codomain_type = Dict(f.codomain, keys=keys)
            def dict_mapper(d: domain_type) -> codomain_type:
                return codomain_type({k: f(v) for k, v in d.items()})
            dict_mapper.__annotations__ = {'d': domain_type, 'return': codomain_type}
            dict_mapper._composed_domain_hint = (domain_type,)
            dict_mapper._composed_codomain_hint = codomain_type
            return Typed(dict_mapper)
        raise TypeError(
            "Wrong type in Dict factory: \n"
            f" ==> {_name(f)}: has unexpected type\n"
             "     [expected_type] Typed"
            f"     [received_type] {_name(type(f))}"
        )

    elif all(isinstance(f, type) for f in args):
        types = args

    elif all(isinstance(t, T) for t in args):
        raise TypeError(
            "Mixed argument types: \n"
            " ==> 'Dict' factory cannot receive both typed functions and types as arguments."
        )
    else:
        for t in args:
            if not isinstance(t, T):
                raise TypeError(
                "Wrong type in 'Dict' factory: \n"
                f" ==> '{_name(t)}': has unexpected type\n"
                 "     [expected_type] TYPE or Typed"
                f"     [received_type] {_name(type(t))}"
            )

    if keys:
        if not isinstance(keys, type):
            raise TypeError(
                "Wrong type in 'Dict' factory: \n"
                f" ==> 'keys': has unexpected type\n"
                 "     [expected_type] TYPE"
                f"     [received_type] {_name(type(keys))}"
            )
        from typed.mods.types.attr import HASHABLE
        if not isinstance(keys, HASHABLE):
            raise TypeError(
                "Wrong type in 'Dict' factory: \n"
                f" ==> 'keys': has unexpected type\n"
                 "     [expected_type] HASHABLE"
                f"     [received_type] {_name(type(keys))}"
            )
    else:
        keys = None

    class _Dict(type(dict)):
        __types__ = types
        __key_type__ = keys

        def __instancecheck__(cls, instance):
            if not isinstance(instance, dict):
                return False
            if not all(isinstance(v, _inner_dict_union(types)) for v in instance.values()):
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

    __null__ = _null_from_list(*types)

    class_name = f"Dict({_name_list(*types)})"
    if keys is not None:
        class_name = f"Dict({_name_list(*types)}, keys={_name(keys)})"
    return _Dict(class_name, (dict,), {
        "__display__": class_name,
        '__types__': types,
        '__key_type__': keys,
        '__null__': {_null(keys): __null__} if keys else {None: __null__}
    })
