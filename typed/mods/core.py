from typed.mods.err import NotDefined, Anonymous
from typed.helper.core import __STATEFUL__, __MAGIC__
from builtins import type as __Type__

def null(t):
    """
    The 'null' polymorphism.
    """
    return getattr(t, "__null__", NotDefined)

def display(t):
    """
    The 'display' polymorphism.
    """
    return getattr(t, "__display__", NotDefined)

def names(*terms):
    return ', '.join(name(t) for t in terms)

def lazy(imports):
    from sys import _getframe
    from importlib import import_module
    from typing import TYPE_CHECKING as __lsp__

    caller_globals = _getframe(1).f_globals
    caller_name = caller_globals.get("__name__", "<unknown>")

    all_names = []
    lazy_map = {}

    for module_path, attr_names in imports.items():
        for attr_name in attr_names:
            all_names.append(attr_name)
            lazy_map[attr_name] = (module_path, attr_name)

    caller_globals["__all__"] = all_names
    caller_globals["__lazy__"] = lazy_map

    def __getattr__(name_str):
        try:
            module_name, attr_name = caller_globals["__lazy__"][name_str]
        except KeyError:
            raise AttributeError(
                f"module {caller_name!r} has no attribute {name_str!r}"
            ) from None

        module = import_module(module_name)
        attr = getattr(module, attr_name)
        caller_globals[name_str] = attr
        return attr

    def __dir__():
        return sorted(set(caller_globals.keys()) | set(caller_globals["__all__"]))

    caller_globals["__getattr__"] = __getattr__
    caller_globals["__dir__"] = __dir__

    return __lsp__

def extends(typ, *others):
    for other in others:
        mro = getattr(other, "__mro__", None)
        if mro is not None:
            if any(base is typ for base in mro):
                return True
    return False

def issup(typ, *others):
    from typed.helper.core import __STATEFUL__
    for other in others:
        if __STATEFUL__.__issup__(typ, other):
            return True
    return False

sup = issup

def issub(typ, *others):
    from typed.helper.core import __STATEFUL__
    for other in others:
        if __STATEFUL__.__issub__(typ, other):
            return True
    return False

sub = issub

def isterm(trm, *types):
    from typed.helper.core import __STATEFUL__
    for t in types:
        if __STATEFUL__.__isterm__(t, trm):
            return True
    return False

term = isterm

class TypeSystem:
    def __init__(
        self,
        universe="__UNIVERSE__",
        abstract="__ABSTRACT__",
        typemap=None,
        __isterm__=__STATEFUL__.__isterm__,
        __issub__=__STATEFUL__.__issub__,
        __in__=__MAGIC__.__in__,
        __eq__=__MAGIC__.__eq__,
        __le__=__MAGIC__.__le__,
        __lt__=__MAGIC__.__lt__,
        __ge__=__MAGIC__.__ge__,
        __gt__=__MAGIC__.__gt__,
        __ne__=__MAGIC__.__ne__
    ):
        self.is_restrictive = True

        self.__members__ = {
            "universe": {},
            "abstract": {},
            "meta": set(),
            "type": set()
        }

        if typemap is None:
            typemap = {}

        self.universe = new.universe(
            name=universe,
            __isterm__=__isterm__,
            __issub__=__issub__,
            __in__=__in__,
            __eq__=__eq__,
            __le__=__le__,
            __lt__=__lt__,
            __ge__=__ge__,
            __gt__=__gt__,
            __ne__=__ne__
        )

        def root_term(typ, trm):
            return "is_abstract" in getattr(trm, "__dict__", {})

        def root_sub(typ, other):
            return "is_abstract" in getattr(other, "__dict__", {})

        self.typemap = typemap

        self.abstract = self.universe(
            abstract,
            (self.universe,),
            {
                "is_abstract": True,
                "level": -1,
                "__isterm__": root_term,
                "__issub__": root_sub,
                "__display__": abstract
            }
        )

        def sub_fn(univ, other):
            if "is_universe" in getattr(other, "__dict__", {}) and "is_universe" in getattr(univ, "__dict__", {}):
                return getattr(other, "level", -1) <= getattr(univ, "level", -1)
            return __issub__(univ, other)

        def abs_sub(abs, other):
            if "is_abstract" in getattr(other, "__dict__", {}) and "is_abstract" in getattr(abs, "__dict__", {}):
                return getattr(other, "level", -1) <= getattr(abs, "level", -1)
            return __issub__(abs, other)

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
                        "__isterm__": __isterm__,
                        "__issub__": sub_fn,
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
                        return __issub__(trm, u_cls)
                    return abs_term

                abs_cls = self.universe(
                    abs_name,
                    (univ_cls,),
                    {
                        "__display__": abs_name,
                        "__isterm__": make_abs_term(univ_cls),
                        "__issub__": abs_sub,
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

    def enrich(self, level):
        while len(self.__members__["universe"]) <= level:
            u, a = next(self.enricher)
            u_level = getattr(u, "level", -1)

            if u_level not in self.__members__["universe"]:
                self.__members__["universe"][u_level] = u
            if u_level not in self.__members__["abstract"]:
                self.__members__["abstract"][u_level] = a

    def add(self, *T):
        for t in T:
            systems = getattr(t, '__typesystems__', [])
            sys_single = getattr(t, '__typesystem__', None)
            if self in systems or self is sys_single:
                if getattr(t, 'is_type', False):
                    self.__members__["type"].add(t)
                if getattr(t, 'is_meta', False):
                    self.__members__["meta"].add(t)

    def rm(self, *T):
        for t in T:
            if t in self.__members__["type"]:
                self.__members__["type"].remove(t)
            if t in self.__members__["meta"]:
                self.__members__["meta"].remove(t)

    def prune(self):
        self.__members__["type"].clear()
        self.__members__["meta"].clear()

    def __contains__(self, X):
        return (
            X in self.__members__["type"] or
            X in self.__members__["meta"] or
            X in self.__members__["abstract"].values() or
            X in self.__members__["universe"].values()
        )

class new:
    """
    Namespace to build typesystem entities.
    """
    @staticmethod
    def universe(
        name="__UNIVERSE__",
        __isterm__=__STATEFUL__.__isterm__,
        __issub__=__STATEFUL__.__issub__,
        __in__=__MAGIC__.__in__,
        __eq__=__MAGIC__.__eq__,
        __le__=__MAGIC__.__le__,
        __lt__=__MAGIC__.__lt__,
        __ge__=__MAGIC__.__ge__,
        __gt__=__MAGIC__.__gt__,
        __ne__=__MAGIC__.__ne__
    ):
        return __Type__(
            name, 
            (__Type__,),
            {
                "is_universe": True,
                "level": -1,
                "__isterm__": __isterm__,
                "__issub__": __issub__,
                "__contains__": __in__,
                "__eq__": __eq__,
                "__le__": __le__,
                "__lt__": __lt__,
                "__ge__": __ge__,
                "__gt__": __gt__,
                "__ne__": __ne__,
                "__hash__": __Type__.__hash__
            }
        )

    @staticmethod
    def typesystem(*args, **kwargs):
        return TypeSystem(*args, **kwargs)

    @staticmethod
    def meta(name, sups=(), attrs={}, typesystem=None):
        if typesystem is None:
            typesystem = TYPESYSTEM
        for sup in sups:
            if sup not in typesystem.__members__["meta"]:
                raise TypeError(f"sup {sup} not in typesystem.__members__['meta']")

        typesystem.enrich(0)
        base_meta = typesystem.__members__["abstract"][0]

        attrs["__display__"] = name
        attrs["is_meta"] = True
        attrs["__typesystems__"] = [typesystem]

        bases = tuple(sups) if sups else (base_meta,)

        M = base_meta(name, bases, attrs)
        typesystem.add(M)
        return M

    @staticmethod
    def type(name, meta, sups=(), attrs={}, typesystem=None):
        if typesystem is None:
            typesystem = TYPESYSTEM
        if meta not in typesystem.__members__["meta"]:
            raise TypeError(f"meta {meta} not in typesystem.__members__['meta']")

        for s in sups:
            if s not in typesystem.__members__["type"]:
                raise TypeError(f"sup {s} not in typesystem.__members__['type']")
            if type(s, typesystem) not in typesystem.__members__["meta"]:
                raise TypeError(f"type(s) not in typesystem.__members__['meta']")

        attrs["__display__"] = name
        attrs["is_type"] = True
        attrs["__typesystems__"] = [typesystem]

        T = meta(name, tuple(sups), attrs)
        typesystem.add(T)
        return T

    @staticmethod
    def err(name):
        from typed.mods.err import Err
        return __Type__(name, (Err,), {"__name__": name, "__display__": name})

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
        if __Type__(typ) in typesystem.__members__["universe"].values():
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

def type(t, typesystem=TYPESYSTEM):
    if typesystem is TYPESYSTEM:
        __typemap__()

    try:
        if t in typesystem.typemap:
            t = typesystem.typemap[t]
    except TypeError:
        pass

    __typ__ = __Type__(t)
    typ = typemap(__typ__, typesystem)

    return typ if typ is not NotDefined else __typ__

def kind(x, typesystem=TYPESYSTEM):
    if any(x is a for a in typesystem.__members__["abstract"].values()):
        return "abstract"
    if any(x is u for u in typesystem.__members__["universe"].values()):
        return "universe"
    if x in typesystem.__members__["meta"]:
        return "meta"
    if x in typesystem.__members__["type"]:
        return "type"
    return NotDefined

def name(t, typesystem=TYPESYSTEM):
    """
    The 'name' polymorphism.
    """
    d = display(t)
    if d is not NotDefined:
        return d

    typ = typemap(t)

    if typ is not NotDefined:
        d = display(typ)
        if d is not NotDefined:
            return d

    return getattr(t, '__name__', Anonymous.__name__)

__UNIVERSE__ = TYPESYSTEM.universe
__UNIVERSE__.__typesystems__ = [TYPESYSTEM]
__UNIVERSE__.__type__ = __Type__

__ABSTRACT__ = TYPESYSTEM.abstract
__ABSTRACT__.__typesystems__ = [TYPESYSTEM]
__ABSTRACT__.__type__ = __Type__

def UNIVERSE(n: int, typesystem=TYPESYSTEM) -> __Type__:
    if n < 0:
        return typesystem.universe

    typesystem.enrich(level=n+1)
    UNI = typesystem.__members__["universe"][n]
    UNI.__typesystems__ = [TYPESYSTEM]
    UNI.__type__ = typesystem.__members__["universe"][n+1]
    UNI.__builtin__ = NotDefined
    UNI.__null__ = NotDefined
    return UNI

def ABSTRACT(n: int, typesystem=TYPESYSTEM) -> __Type__:
    if n < 0:
        return typesystem.abstract

    typesystem.enrich(level=n+1)
    ABS = typesystem.__members__["abstract"][n]
    ABS.__typesystems__ = [TYPESYSTEM]
    ABS.__type__ = typesystem.__members__["universe"][n+1]
    ABS.__builtin__ = NotDefined
    ABS.__null__ = NotDefined
    return ABS
