import re
from functools import lru_cache as cache
from typed.mods.types.func import Typed
from typed.mods.helper.null import  _null, _null_from_list
from typed.mods.helper.helper import (
    _name,
    _name_list,
    _inner_union,
    _inner_dict_union
)

@cache
def Union(*args):
    """
    Build the 'union' of types:
        > an object 'p' of 'Union(X, Y, ...)'
        > is an object of some of 'X, Y, ...'
    Can be applied to typed functions:
        > 'Union(f, g, ...): Union(f.domain, g.domain) -> Union(f.codomain, g.codomain)'
    """
    from typed.mods.types.base import TYPE
    from typed.mods.meta.base  import __UNIVERSE__
    T = (Typed, TYPE, __UNIVERSE__)
    if args and all(isinstance(f, TYPE) for f in args):
        unique_types = set(args)
        def _key(t):
            return (t.__module__, getattr(t, '__qualname__', t.__name__))
        sorted_types = tuple(sorted(unique_types, key=_key))
        if len(sorted_types) == 1:
            return sorted_types[0]
        if sorted_types != args:
            return Union(*sorted_types)

    if not args:
        return TYPE(None)
    if all((not isinstance(f, TYPE)) and isinstance(f, Typed) for f in args):
        funcs = args
        domains = [f.domain for f in funcs]
        codomains = [f.codomain for f in funcs]
        dom_types = [d[0] if len(d) == 1 else d for d in domains]
        if any(not (isinstance(f, Typed) and not isinstance(f, TYPE)) for f in funcs):
            raise TypeError(
                "Wrong type in Union factory: \n"
                f" ==> {_name(f)}: has unexpected type\n"
                 "     [expected_type] Typed"
                f"     [received_type] {_name(TYPE(f))}"
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

    elif all(isinstance(f, (TYPE, __UNIVERSE__)) for f in args):
        types = tuple(dict.fromkeys(args))
        if len(types) == 1:
            return types[0]
    elif all(isinstance(t, T) for t in args):
        for t in args:
            if isinstance(t, Typed):
                raise TypeError(
                    "Mixed types in Union factory:\n"
                    f" ==> '{_name(t)}': it is a typed function."
                     "     [received_type] subtype of Typed\n"
                     "     [expected_type] subtype of TYPE or __UNIVERSE__"
                )
    else:
        for t in args:
            if not isinstance(t, T):
                raise TypeError(
                    "Wrong type in Union factory: \n"
                    f" ==> {_name(t)}: has unexpected type\n"
                     "     [expected_type] TYPE, __UNIVERSE__ or Typed\n"
                    f"     [received_type] {_name(TYPE(t))}"
                )

    from typed.mods.meta.base import _TYPE_
    class UNION(_TYPE_):
        def __instancecheck__(cls, instance):
            return any(isinstance(instance, t) for t in cls.__types__)
        def __subclasscheck__(cls, subclass):
            if subclass is cls:
                return True
            if hasattr(subclass, '__types__'):
                return all(any(issubclass(st, ct) for ct in cls.__types__)
                           for st in subclass.__types__)
            return any(issubclass(subclass, t) for t in cls.__types__)

    class_name = f"Union({_name_list(*types)})"

    __null__ = _null_from_list(*types)

    return UNION(class_name, (), {
        '__display__': class_name,
        '__types__': types,
        '__null__': __null__,
    })

@cache
def Prod(*args):
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

    class PROD(type):
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
    return PROD(class_name, (tuple,), {
        "__display__": class_name,
        '__types__': types,
        '__new__': prod_new,
        "__null__": tuple(_null(t) for t in types)
    })

@cache
def UProd(*args):
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

    class UPROD(type):
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
    return UPROD(class_name, (tuple,), {
        "__display__": class_name,
        '__types__': types,
        "__null__": set(_null(t) for t in types)
    })
