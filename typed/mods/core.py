import sys
import importlib
from typing import TYPE_CHECKING as __lsp__
from typed.mods.err import NotDefined
from builtins import type as __Type__

def null(typ):
    return getattr(typ, "__null__", NotDefined)

def display(typ):
    return getattr(typ, "__display__", NotDefined)

def name(trm):
    d = display(trm)
    if d is not NotDefined:
        return d

    typ = typemap(trm)

    if typ is not NotDefined:
        d = display(typ)
        if d is not NotDefined:
            return d

    return getattr(trm, '__name__', "Anonymous")

def names(*terms):
    return ', '.join(name(t) for t in terms)

def lazy(imports):
    caller_globals = sys._getframe(1).f_globals
    caller_name = caller_globals.get("__name__", "<unknown>")

    all_names = list(imports.keys())
    caller_globals["__all__"] = all_names

    lazy_map = {}
    for name_key, module_path in imports.items():
        if name_key == "dt" and "datetime" in imports and imports["datetime"] == module_path:
            lazy_map[name_key] = (imports["datetime"], "datetime")
        else:
            lazy_map[name_key] = (module_path, name_key)

    caller_globals["__lazy__"] = lazy_map

    def __getattr__(name_str):
        try:
            module_name, attr_name = caller_globals["__lazy__"][name_str]
        except KeyError:
            raise AttributeError(
                f"module {caller_name!r} has no attribute {name_str!r}"
            ) from None

        module = importlib.import_module(module_name)
        attr = getattr(module, attr_name)
        caller_globals[name_str] = attr
        return attr

    def __dir__():
        return sorted(set(caller_globals.keys()) | set(caller_globals["__all__"]))

    caller_globals["__getattr__"] = __getattr__
    caller_globals["__dir__"] = __dir__

    return __lsp__

_sub_visiting = set()

def sup(typ, other):
    mro = getattr(other, "__mro__", None)
    if mro is not None:
        return any(base is typ for base in mro)
    return False

def __sub__(typ, other):
    key = (id(typ), id(other))
    if key in _sub_visiting:
        return False
    _sub_visiting.add(key)
    try:
        if sup(typ, other):
            return True

        if "__sub__" in getattr(typ, "__dict__", {}):
            sub_func = typ.__dict__["__sub__"]
            if sub_func is not __sub__:
                res = sub_func(typ, other)
                if res is not NotImplemented: return res

        if "__sub__" in getattr(other, "__dict__", {}):
            sub_func = other.__dict__["__sub__"]
            if sub_func is not __sub__:
                res = sub_func(other, typ)
                if res is not NotImplemented: return res

        meta_typ = type(typ)
        if hasattr(meta_typ, "__sub__"):
            sub_func = getattr(meta_typ, "__sub__")
            if sub_func is not __sub__:
                res = sub_func(typ, other)
                if res is not NotImplemented: return res

        meta_other = type(other)
        if hasattr(meta_other, "__sub__"):
            sub_func = getattr(meta_other, "__sub__")
            if sub_func is not __sub__:
                res = sub_func(other, typ)
                if res is not NotImplemented: return res

        return False
    finally:
        _sub_visiting.remove(key)

_term_visiting = set()

def __term__(typ, trm):
    key = (id(typ), id(trm))
    if key in _term_visiting:
        return False
    _term_visiting.add(key)
    try:
        if "__term__" in getattr(typ, "__dict__", {}):
            term_func = typ.__dict__["__term__"]
            if term_func is not __term__:
                res = term_func(typ, trm)
                if res is not NotImplemented: return res

        meta = type(typ)
        if hasattr(meta, "__term__"):
            term_func = getattr(meta, "__term__")
            if term_func is not __term__:
                res = term_func(typ, trm)
                if res is not NotImplemented: return res

        if "__sub__" in getattr(typ, "__dict__", {}):
            sub_func = typ.__dict__["__sub__"]
            if sub_func is not __sub__:
                res = sub_func(typ, type(trm))
                if res: return True

        if hasattr(meta, "__sub__"):
            sub_func = getattr(meta, "__sub__")
            if sub_func is not __sub__:
                res = sub_func(typ, type(trm))
                if res: return True

        if isinstance(trm, type) and isinstance(typ, type):
            if issubclass(trm, typ):
                return True

        return isinstance(trm, typ)
    finally:
        _term_visiting.remove(key)

def sub(other, typ):
    return __sub__(typ, other)

def term(trm, typ):
    return __term__(typ, trm)

def __in__(typ, trm):
    return __term__(typ, trm)

def __le__(typ, other):
    return __sub__(typ, other)

def __lt__(typ, other):
    return __sub__(typ, other) and not __sub__(other, typ)

def __ge__(typ, other):
    return __sub__(other, typ)

def __gt__(typ, other):
    return __sub__(other, typ) and not __sub__(typ, other)

def __eq__(typ, other):
    return __sub__(typ, other) and __sub__(other, typ)

def __ne__(typ, other):
    return not __eq__(typ, other)

class new:
    def universe(
        name="__UNIVERSE__",
        __term__=__term__,
        __sub__=__sub__,
        __in__=__in__,
        __eq__=__eq__,
        __le__=__le__,
        __lt__=__lt__,
        __ge__=__ge__,
        __gt__=__gt__,
        __ne__=__ne__
    ):
        return __Type__(
            name, 
            (__Type__,),
            {
                "is_universe": True,
                "level": -1,
                "__term__": __term__,
                "__sub__": __sub__,
                "__contains__": __in__,
                "__eq__": __eq__,
                "__le_":__le__,
                "__lt_":__lt__,
                "__ge_": __ge__,
                "__gt_": __gt__,
                "__ne__": __ne__,
                "__hash__": __Type__.__hash__
            }
        )

    class typesystem:
        def __init__(
            self,
            universe="__UNIVERSE__",
            abstract="__ABSTRACT__",
            typemap=None,
            __term__=__term__,
            __sub__=__sub__,
            __in__=__in__,
            __eq__=__eq__,
            __le__=__le__,
            __lt__=__lt__,
            __ge__=__ge__,
            __gt__=__gt__,
            __ne__=__ne__
        ):
            if typemap is None:
                typemap = {}

            self.universe = new.universe(
                name=universe,
                __term__=__term__,
                __sub__=__sub__,
                __in__=__in__,
                __eq__=__eq__,
                __le__=__le__,
                __lt__=__lt__,
                __ge__=__ge__,
                __gt__=__gt__,
                __ne__=__ne__
            )

            def root_term(typ, trm):
                return getattr(trm, "is_abstract", False)

            def root_sub(typ, other):
                return getattr(other, "is_abstract", False)

            self.typemap = typemap

            self.abstract = self.universe(
                abstract,
                (self.universe,),
                {
                    "is_abstract": True,
                    "level": -1,
                    "__term__": root_term,
                    "__sub__": root_sub,
                    "__display__": abstract
                }
            )

            self.__universes__ = {}
            self.__abstracts__ = {}

            def sub(univ, other):
                if hasattr(other, "is_universe"):
                    return getattr(other, "level", -1) <= getattr(univ, "level", -1)
                return __sub__(univ, other)

            def abs_sub(abs, other):
                if getattr(other, "is_abstract", False):
                    return getattr(other, "level", -1) <= getattr(abs, "level", -1)
                return __sub__(abs, other)

            def __new__(univ, typ, bases, namespace, **kwds):
                return __Type__.__new__(univ, typ, bases, namespace, **kwds)

            def enricher():
                level = 0
                prev = None
                prev_abs = None

                while True:
                    univ_name = f"UNIVERSE({level})"
                    abs_name  = f"ABSTRACT({level})"

                    univ_cls = self.universe(
                        univ_name,
                        (__Type__,),
                        {
                            "__term__": __term__,
                            "__sub__": sub,
                            "__new__": __new__,
                            "__contains__": __in__,
                            "__eq__": __eq__,
                            "__le__": __le__,
                            "__lt__": __lt__,
                            "__ge__": __ge__,
                            "__gt__": __gt__,
                            "__ne__": __ne__,
                            "level": level,
                            "__display__": univ_name,
                            "is_universe": True,
                            "__hash__": __Type__.__hash__
                        }
                    )

                    def make_abs_term(u_cls):
                        def abs_term(typ, trm):
                            return __sub__(trm, u_cls)
                        return abs_term

                    abs_cls = self.universe(
                        abs_name,
                        (univ_cls,),
                        {
                            "__display__": abs_name,
                            "__term__": make_abs_term(univ_cls),
                            "__sub__": abs_sub,
                            "is_abstract": True,
                            "level": level
                        }
                    )

                    if prev is not None:
                        prev.__class__ = univ_cls
                    if prev_abs is not None:
                        prev_abs.__class__ = univ_cls

                    prev = univ_cls
                    prev_abs = abs_cls

                    yield univ_cls, abs_cls
                    level += 1

            self.enricher = enricher()

        def populate(self, level):
            while len(self.__universes__) <= level:
                u, a = next(self.enricher)
                u_level = getattr(u, "level", -1)

                if u_level not in self.__universes__:
                    self.__universes__[u_level] = u
                if u_level not in self.__abstracts__:
                    self.__abstracts__[u_level] = a

    def meta():
        pass

    def type():
        pass

    def err(name):
        from typed.mods.err import Err
        return new.type(name, (Err,), {"__name__": name, "__display__": name})

TYPESYSTEM = new.typesystem()

def __typemap__():
    from builtins import (
        int       as __Int__,
        float     as __Float__,
        bool      as __Bool__,
        str       as __Str__,
        bytes     as __Bytes__,
        bytearray as __ByteArray__,
        list      as __List__,
        tuple     as __Tuple__,
        set       as __Set__,
        dict      as __Dict__,
        type      as __Type__
    )
    from typed.mods.types.base import (
        Int, Float, Bool, Str, Bytes,
        List, Tuple, Set, Dict
    )
    TYPESYSTEM.typemap[__Int__]       = Int
    TYPESYSTEM.typemap[__Float__]     = Float
    TYPESYSTEM.typemap[__Bool__]      = Bool
    TYPESYSTEM.typemap[__Str__]       = Str
    TYPESYSTEM.typemap[__Bytes__]     = Bytes
    TYPESYSTEM.typemap[__ByteArray__] = Bytes
    TYPESYSTEM.typemap[__List__]      = List
    TYPESYSTEM.typemap[__Tuple__]     = Tuple
    TYPESYSTEM.typemap[__Set__]       = Set
    TYPESYSTEM.typemap[__Dict__]      = Dict
    TYPESYSTEM.typemap[__Type__]      = TYPESYSTEM.universe

def typemap(typ, typesystem=TYPESYSTEM):
    try:
        if __Type__(typ) in typesystem.__universes__:
            return typ
    except TypeError:
        pass

    if typesystem is TYPESYSTEM:
        __typemap__()

    try:
        if typ in typesystem.typemap:
            return typesystem.typemap[typ]
    except TypeError:
        pass

    return NotDefined

def type(trm, typesystem=TYPESYSTEM):
    if typesystem is TYPESYSTEM:
        __typemap__()

    try:
        if trm in typesystem.typemap:
            trm = typesystem.typemap[trm]
    except TypeError:
        pass

    __typ__ = __Type__(trm)
    typ = typemap(__typ__, typesystem)

    return typ if typ is not NotDefined else __typ__
