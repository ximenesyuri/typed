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
def _Tuple_(*args):
    from typed.mods.types.base import TYPE
    if args and all(isinstance(t, TYPE) for t in args):
        unique = set(args)
        def _key(t):
            return (t.__module__, getattr(t, '__qualname__', t.__name__))
        sorted_types = tuple(sorted(unique, key=_key))
        if len(sorted_types) == 1:
            return sorted_types[0]
        if sorted_types != args:
            return _Tuple_(*sorted_types)
    if not args:
        return type(None)
    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], TYPE):
        f = args[0]
        if isinstance(f, Typed):
            domain_type = _Tuple_(*f.domain)
            codomain_type = _Tuple_(f.codomain)

            def tuple_mapper(xs: domain_type) -> codomain_type:
                return codomain_type(*(f(x) for x in xs))

            tuple_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
            tuple_mapper._composed_domain_hint = (domain_type,)
            tuple_mapper._composed_codomain_hint = codomain_type
            return Typed(tuple_mapper)

        raise TypeError(
            "Argument with unexpected type in Tuple factory.\n"
            f" ==> '{_name(f)}' has wrong type.\n"
             "     [expected_type] Typed\n"
            f"     [received_type] {_name(TYPE(f))}"
        )
    elif all(isinstance(f, TYPE) for f in args):
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
                 "     [expected_type] TYPE or Typed\n"
                f"     [received_type] {_name(TYPE(t))}"
            )

    from typed.mods.meta.base import TUPLE
    from typed.mods.types.base import Tuple
    __null__ = _null_from_list(*types)
    class_name = f"Tuple({_name_list(*types)})"
    return TUPLE(class_name, (Tuple,), {
        '__display__': class_name,
        '__types__': types,
        '__convert__': staticmethod(TUPLE.__convert__),
        '__null__': (__null__,) if __null__ is not None else None
    })

@cache
def _List_(*args):
    from typed.mods.types.base import TYPE
    if args and all(isinstance(t, TYPE) for t in args):
        unique = set(args)
        def _key(t):
            return (t.__module__, getattr(t, '__qualname__', t.__name__))
        sorted_types = tuple(sorted(unique, key=_key))
        if sorted_types != args:
            return _List_(*sorted_types)
    if not args:
        return type(None)
    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], TYPE):
        f = args[0]
        if isinstance(f, Typed):
            domain_type = _List_(*f.domain)
            codomain_type = _List_(f.codomain)
            def list_mapper(xs: domain_type) -> codomain_type:
                return codomain_type(*(f(x) for x in xs))
            list_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
            list_mapper._composed_domain_hint = (domain_type,)
            list_mapper._composed_codomain_hint = codomain_type
            return Typed(list_mapper)
        raise TypeError(
            "Argument with unexpected type in Tuple factory.\n"
            f" ==> '{_name(f)}' has wrong type.\n"
             "     [expected_type] Typed\n"
            f"     [received_type] {_name(TYPE(f))}"
        )

    elif all(isinstance(f, TYPE) for f in args):
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
                 "     [expected_type] TYPE or Typed\n"
                f"     [received_type] {_name(TYPE(t))}"
            )

    __null__ = _null_from_list(*types)
    from typed.mods.meta.base import LIST
    class_name = f"List({_name_list(*types)})"
    from typed.mods.types.base import List
    return LIST(class_name, (List,), {
        '__display__': class_name,
        '__types__': types,
        '__convert__': staticmethod(LIST.__convert__),
        '__null__': [__null__,] if __null__ is not None else None
    })

@cache
def _Set_(*args):
    from typed.mods.types.base import TYPE
    if args and all(isinstance(t, TYPE) for t in args):
        unique = set(args)
        def _key(t):
            return (t.__module__, getattr(t, '__qualname__', t.__name__))
        sorted_types = tuple(sorted(unique, key=_key))
        if len(sorted_types) == 1:
            return sorted_types[0]
        if sorted_types != args:
            return _Set_(*sorted_types)

    if not args:
        return type(None)
    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], TYPE):
        f = args[0]
        if isinstance(f, Typed):
            domain_type = _Set_(*f.domain)
            codomain_type = _Set_(f.codomain)
            def set_mapper(xs: domain_type) -> codomain_type:
                return codomain_type(*(f(x) for x in xs))
            set_mapper.__annotations__ = {'xs': domain_type, 'return': codomain_type}
            set_mapper._composed_domain_hint = (domain_type,)
            set_mapper._composed_codomain_hint = codomain_type
            return Typed(set_mapper)
        raise TypeError(
            "Wrong type in Union factory: \n"
            f" ==> {_name(f)}: has unexpected type\n"
             "     [expected_type] Typed\n"
            f"     [received_type] {_name(TYPE(f))}"
        )

    elif all(isinstance(f, TYPE) for f in args):
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
                 "     [expected_type] TYPE or Typed\n"
                f"     [received_type] {_name(TYPE(t))}"
            )

    __null__ = _null_from_list(*types)
    from typed.mods.meta.base import SET
    class_name = f"Set({_name_list(*types)})"
    from typed.mods.types.base import Set
    return SET(class_name, (Set,), {
        '__display__': class_name,
        '__types__': types,
        '__convert__': staticmethod(SET.__convert__),
        '__null__': set(__null__) if __null__ is not None else None
    })

@cache
def _Dict_(*args, keys=None):
    from typed.mods.types.base import TYPE
    if args and all(isinstance(t, TYPE) for t in args):
        unique = set(args)
        def _key(t):
            return (t.__module__, getattr(t, '__qualname__', t.__name__))
        sorted_types = tuple(sorted(unique, key=_key))
        if sorted_types != args:
            return _Dict_(*sorted_types, keys=keys)

    if not args:
        return type(None)

    if len(args) == 1 and (callable(args[0]) or hasattr(args[0], 'func')) and not isinstance(args[0], TYPE):
        f = args[0]
        if isinstance(f, Typed):
            domain_type = _Dict_(f.domain, keys=keys)
            codomain_type = _Dict_(f.codomain, keys=keys)
            def dict_mapper(d: domain_type) -> codomain_type:
                return codomain_type({k: f(v) for k, v in d.items()})
            dict_mapper.__annotations__ = {'d': domain_type, 'return': codomain_type}
            dict_mapper._composed_domain_hint = (domain_type,)
            dict_mapper._composed_codomain_hint = codomain_type
            return Typed(dict_mapper)
        raise TypeError(
            "Wrong type in Dict factory: \n"
            f" ==> {_name(f)}: has unexpected type\n"
             "     [expected_type] Typed\n"
            f"     [received_type] {_name(TYPE(f))}"
        )

    elif all(isinstance(f, TYPE) for f in args):
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
                 "     [expected_type] TYPE or Typed\n"
                f"     [received_type] {_name(TYPE(t))}"
            )

    if keys:
        if not isinstance(keys, TYPE):
            raise TypeError(
                "Wrong type in 'Dict' factory: \n"
                f" ==> 'keys': has unexpected type\n"
                 "     [expected_type] TYPE\n"
                f"     [received_type] {_name(TYPE(keys))}"
            )
        from typed.mods.types.attr import HASHABLE
        if not isinstance(keys, HASHABLE):
            raise TypeError(
                "Wrong type in 'Dict' factory: \n"
                f" ==> 'keys': has unexpected type\n"
                 "     [expected_type] HASHABLE\n"
                f"     [received_type] {_name(TYPE(keys))}"
            )
    else:
        keys = None

    __null__ = _null_from_list(*types)
    from typed.mods.meta.base import DICT
    class_name = f"Dict({_name_list(*types)})"
    if keys is not None:
        class_name = f"Dict({_name_list(*types)}, keys={_name(keys)})"
    from typed.mods.types.base import Dict
    return DICT(class_name, (Dict,), {
        "__display__": class_name,
        '__types__': types,
        '__key_type__': keys,
        '__convert__': staticmethod(DICT.__convert__),
        '__null__': {_null(keys): __null__} if keys else {'': __null__},
        '__doc__': DICT.__doc__
    })
