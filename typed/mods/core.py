def null(t):
    """
    The 'null' polymorphism.
    """
    from typed.mods.err import NotDefined
    return getattr(t, "__null__", NotDefined)

def display(t):
    """
    The 'display' polymorphism.
    """
    from typed.mods.err import NotDefined
    return getattr(t, "__display__", NotDefined)

def builtin(t):
    """
    The 'builtin' polymorphism.
    """
    from typed.mods.err import NotDefined
    return getattr(t, "__builtin__", NotDefined)

def track(t):
    from typed.mods.err import NotDefined
    if builtin(t) is not NotDefined:
        name = f"Track({name(t)})"
        attrs = {
            "__display__": name,
            "is_track": True,
            "__builtin__": t
        }
        return type.__call__(name, (t,), attrs)

    return NotDefined

def terms(t):
    """
    The 'terms' polymorphism.
    """
    from typed.mods.err import NotDefined
    __terms__ = getattr(t, "__terms__", NotDefined)
    if __terms__ is not NotDefined:
        return set(__terms__)
    return

def names(*terms):
    return ', '.join(name(t) for t in terms)

def extends(typ, *others):
    for other in others:
        mro = getattr(other, "__mro__", None)
        if mro is not None:
            if any(base is typ for base in mro):
                return True
    return False

def issup(typ, *others):
    from typed.helper.core import STATEFUL
    for other in others:
        if STATEFUL.__issup__(typ, other):
            return True
    return False

def issub(typ, *others):
    from typed.helper.core import STATEFUL
    for other in others:
        if STATEFUL.__issub__(typ, other):
            return True
    return False

def isterm(trm, *types):
    from typed.helper.core import STATEFUL
    for t in types:
        if STATEFUL.__isterm__(t, trm):
            return True
    return False

class ___UNIVERSE___(type):
    def __new__(mcls, name, bases, dct, **kwds):
        cls = super().__new__(mcls, name, bases, dct, **kwds)

        if "__terms__" not in mcls.__dict__:
            from weakref import WeakSet
            cls.__terms__ = WeakSet()

        if "__terms__" not in mcls.__dict__:
            from weakref import WeakSet
            mcls.__terms__ = WeakSet()

        try:
            mcls.__terms__.add(cls)
        except AttributeError:
            pass

        return cls

    def __iter__(cls):
        systems = getattr(cls, "__typesystems__", [])
        for typesystem in systems:
            yield from typesystem.__members__["universe"].values()


class ___ABSTRACT___(___UNIVERSE___):
    def __new__(mcls, name, bases, dct, **kwds):
        cls = super().__new__(mcls, name, bases, dct, **kwds)

        if "__terms__" not in mcls.__dict__:
            from weakref import WeakSet
            cls.__terms__ = WeakSet()

        if "__terms__" not in mcls.__dict__:
            from weakref import WeakSet
            mcls.__terms__ = WeakSet()

        try:
            mcls.__terms__.add(cls)
        except AttributeError:
            pass

        return cls

    def __iter__(cls):
        systems = getattr(cls, "__typesystems__", [])
        for typesystem in systems:
            yield from typesystem.__members__["abstract"].values()


class __UNIVERSE__(type, metaclass=___UNIVERSE___):
    def __new__(mcls, name, bases, dct, **kwds):
        cls = super().__new__(mcls, name, bases, dct, **kwds)

        if "__terms__" not in mcls.__dict__:
            from weakref import WeakSet
            cls.__terms__ = WeakSet()

        if "__terms__" not in mcls.__dict__:
            from weakref import WeakSet
            mcls.__terms__ = WeakSet()

        try:
            mcls.__terms__.add(cls)
        except AttributeError:
            pass

        return cls

    def __iter__(typ):
        from typed.helper.core import MAGIC
        return MAGIC.__iter__(typ)

    def __call__(typ, *args, typesystem=None, **kwargs):
        if len(args) == 3 and isinstance(args[0], str) and isinstance(args[1], tuple) and isinstance(args[2], dict):
            return super().__call__(*args, **kwargs)

        if typesystem is None:
            typesystem = TYPESYSTEM

        from typed.mods.err import NotDefined
        if len(args) == 1 and isinstance(args[0], int):
            n = args[0]
            if n < 0:
                return typesystem.universe

            typesystem.enrich(level=n+1)
            UNI = typesystem.__members__["universe"][n]
            UNI.__typesystems__ = [typesystem]
            UNI.__type__ = typesystem.__members__["universe"][n+1]
            UNI.__builtin__ = NotDefined
            UNI.__null__ = NotDefined
            return UNI

        if len(args) == 0 and typesystem is not NotDefined:
            return typesystem.universe

        return super().__call__(*args, **kwargs)


class __ABSTRACT__(__UNIVERSE__, metaclass=___ABSTRACT___):
    def __iter__(typ):
        from typed.helper.core import MAGIC
        return MAGIC.__iter__(typ)

    def __call__(typ, *args, typesystem=None, **kwargs):
        if len(args) == 3 and isinstance(args[0], str) and isinstance(args[1], tuple) and isinstance(args[2], dict):
            return super().__call__(*args, **kwargs)

        if typesystem is None:
            typesystem = TYPESYSTEM

        if len(args) == 1 and isinstance(args[0], int):
            n = args[0]
            if n < 0:
                return typesystem.abstract

            from typed.mods.err import NotDefined
            typesystem.enrich(level=n+1)
            ABS = typesystem.__members__["abstract"][n]
            ABS.__typesystems__ = [typesystem]
            ABS.__type__ = typesystem.__members__["universe"][n+1]
            ABS.__builtin__ = NotDefined
            ABS.__null__ = NotDefined
            return ABS

        if len(args) == 0 and typesystem is not NotDefined:
            return typesystem.abstract

        return super().__call__(*args, **kwargs)


class __TYPESYSTEM__:
    def __init__(
        self,
        universe="__UNIVERSE__",
        abstract="__ABSTRACT__",
        typemap=None,
        __isterm__=None,
        __issub__=None,
        __in__=None,
        __eq__=None,
        __le__=None,
        __lt__=None,
        __ge__=None,
        __gt__=None,
        __ne__=None
    ):
        self.is_restrictive = True

        if None in (__isterm__, __issub__):
            from typed.helper.core import STATEFUL

        if None in (__in__, __eq__, __le__, __lt__, __ge__, __gt__, __ne__):
            from typed.helper.core import MAGIC

        __isterm__ = __isterm__ if __isterm__ is not None else STATEFUL.__isterm__
        __issub__ = __issub__ if __issub__ is not None else STATEFUL.__issub__
        __in__ = __in__ if __in__ is not None else MAGIC.__in__
        __eq__ = __eq__ if __eq__ is not None else MAGIC.__eq__
        __le__ = __le__ if __le__ is not None else MAGIC.__le__
        __lt__ = __lt__ if __lt__ is not None else MAGIC.__lt__
        __ge__ = __ge__ if __ge__ is not None else MAGIC.__ge__
        __gt__ = __gt__ if __gt__ is not None else MAGIC.__gt__
        __ne__ = __ne__ if __ne__ is not None else MAGIC.__ne__

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
            __ne__=__ne__,
            __display__=universe
        )

        self.universe.__typesystems__ = [self]
        self.universe.__type__ = type

        self.__members__["universe"][-1] = self.universe

        def root_term(typ, trm):
            return "is_abstract" in getattr(trm, "__dict__", {})

        def root_sub(typ, other):
            return "is_abstract" in getattr(other, "__dict__", {})

        self.typemap = typemap

        self.abstract = new.abstract(
            name=abstract,
            bases=(self.universe,),
            __isterm__=root_term,
            __issub__=root_sub,
            __in__=__in__,
            __eq__=__eq__,
            __le__=__le__,
            __lt__=__lt__,
            __ge__=__ge__,
            __gt__=__gt__,
            __ne__=__ne__,
            __display__=abstract
        )

        self.abstract.__typesystems__ = [self]
        self.abstract.__type__ = type

        self.__members__["abstract"][-1] = self.abstract

        def sub_fn(univ, other):
            if "is_universe" in getattr(other, "__dict__", {}) and "is_universe" in getattr(univ, "__dict__", {}):
                return getattr(other, "level", -1) <= getattr(univ, "level", -1)
            return __issub__(univ, other)

        def abs_sub(abs, other):
            if "is_abstract" in getattr(other, "__dict__", {}) and "is_abstract" in getattr(abs, "__dict__", {}):
                return getattr(other, "level", -1) <= getattr(abs, "level", -1)
            return __issub__(abs, other)

        def __new__(univ, typ, bases, namespace, **kwds):
            cls = type.__new__(univ, typ, bases, namespace, **kwds)

            if "__terms__" not in cls.__dict__:
                from weakref import WeakSet
                cls.__terms__ = WeakSet()
            if "__terms__" not in univ.__dict__:
                from weakref import WeakSet
                univ.__terms__ = WeakSet()
            try:
                univ.__terms__.add(cls)
            except AttributeError:
                pass
            return cls

        def enricher():
            level = 0
            prev = None
            prev_abs = None

            while True:
                univ_name = f"UNIVERSE({level})"
                abs_name  = f"ABSTRACT({level})"

                univ_cls = new.universe(
                    name=univ_name,
                    bases=(type,),
                    __isterm__=__isterm__,
                    __issub__=sub_fn,
                    __in__=__in__,
                    __eq__=__eq__,
                    __le__=__le__,
                    __lt__=__lt__,
                    __ge__=__ge__,
                    __gt__=__gt__,
                    __ne__=__ne__,
                    __new__=__new__,
                    level=level,
                    __display__=univ_name
                )

                def make_abs_term(u_cls):
                    def abs_term(typ, trm):
                        return __issub__(trm, u_cls)
                    return abs_term

                abs_cls = new.abstract(
                    name=abs_name,
                    bases=(univ_cls,),
                    __isterm__=make_abs_term(univ_cls),
                    __issub__=abs_sub,
                    __in__=__in__,
                    __eq__=__eq__,
                    __le__=__le__,
                    __lt__=__lt__,
                    __ge__=__ge__,
                    __gt__=__gt__,
                    __ne__=__ne__,
                    level=level,
                    __display__=abs_name
                )

                if hasattr(self.universe, "__terms__"):
                    self.universe.__terms__.add(univ_cls)
                if hasattr(self.abstract, "__terms__"):
                    self.abstract.__terms__.add(abs_cls)

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
        while len(self.__members__["universe"]) <= level + 1:
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

    def __iter__(self):
        yield from self.__members__["universe"].values()
        yield from self.__members__["abstract"].values()
        yield from self.__members__["meta"]
        yield from self.__members__["type"]

class new:
    @staticmethod
    def universe(
        name="UNIVERSE",
        bases=(type,),
        __isterm__=None,
        __issub__=None,
        __in__=None,
        __eq__=None,
        __le__=None,
        __lt__=None,
        __ge__=None,
        __gt__=None,
        __ne__=None,
        __iter__=None,
        **kwargs
    ):

        if None in (__isterm__, __issub__):
            from typed.helper.core import STATEFUL

        if None in (__in__, __eq__, __le__, __lt__, __ge__, __gt__, __ne__, __iter__):
            from typed.helper.core import MAGIC

        __isterm__ = __isterm__ if __isterm__ is not None else STATEFUL.__isterm__
        __issub__ = __issub__ if __issub__ is not None else STATEFUL.__issub__
        __in__ = __in__ if __in__ is not None else MAGIC.__in__
        __eq__ = __eq__ if __eq__ is not None else MAGIC.__eq__
        __le__ = __le__ if __le__ is not None else MAGIC.__le__
        __lt__ = __lt__ if __lt__ is not None else MAGIC.__lt__
        __ge__ = __ge__ if __ge__ is not None else MAGIC.__ge__
        __gt__ = __gt__ if __gt__ is not None else MAGIC.__gt__
        __ne__ = __ne__ if __ne__ is not None else MAGIC.__ne__
        __iter__ = __iter__ if __iter__ is not None else MAGIC.__iter__

        from builtins import type as __Type__
        attrs = {
            "is_universe": True,
            "is_universe_parametric": True,
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
            "__iter__": __iter__,
            "__hash__": __Type__.__hash__
        }
        attrs.update(kwargs)
        return __UNIVERSE__(name, bases, attrs)

    @staticmethod
    def abstract(
        name="ABSTRACT",
        bases=(type,),
        __isterm__=None,
        __issub__=None,
        __in__=None,
        __eq__=None,
        __le__=None,
        __lt__=None,
        __ge__=None,
        __gt__=None,
        __ne__=None,
        __iter__=None,
        **kwargs
    ):

        if None in (__isterm__, __issub__):
            from typed.helper.core import STATEFUL

        if None in (__in__, __eq__, __le__, __lt__, __ge__, __gt__, __ne__, __iter__):
            from typed.helper.core import MAGIC

        __isterm__ = __isterm__ if __isterm__ is not None else STATEFUL.__isterm__
        __issub__ = __issub__ if __issub__ is not None else STATEFUL.__issub__
        __in__ = __in__ if __in__ is not None else MAGIC.__in__
        __eq__ = __eq__ if __eq__ is not None else MAGIC.__eq__
        __le__ = __le__ if __le__ is not None else MAGIC.__le__
        __lt__ = __lt__ if __lt__ is not None else MAGIC.__lt__
        __ge__ = __ge__ if __ge__ is not None else MAGIC.__ge__
        __gt__ = __gt__ if __gt__ is not None else MAGIC.__gt__
        __ne__ = __ne__ if __ne__ is not None else MAGIC.__ne__
        __iter__ = __iter__ if __iter__ is not None else MAGIC.__iter__

        from builtins import type as __Type__
        attrs = {
            "is_abstract": True,
            "is_abstract_parametric": True,
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
            "__iter__": __iter__,
            "__hash__": __Type__.__hash__
        }
        attrs.update(kwargs)
        return __ABSTRACT__(name, bases, attrs)

    @staticmethod
    def typesystem(*args, **kwargs):
        return __TYPESYSTEM__(*args, **kwargs)

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
        return type(name, (Err,), {"__name__": name, "__display__": name})

TYPESYSTEM = new.typesystem()

def __typemap__():
    from typed.mods.types.base import (
        Int, Float, Bool, Str, Bytes,
        List, Tuple, Set, Dict
    )
    TYPESYSTEM.typemap[int]       = Int
    TYPESYSTEM.typemap[float]     = Float
    TYPESYSTEM.typemap[bool]      = Bool
    TYPESYSTEM.typemap[str]       = Str
    TYPESYSTEM.typemap[bytes]     = Bytes
    TYPESYSTEM.typemap[bytearray] = Bytes
    TYPESYSTEM.typemap[list]      = List
    TYPESYSTEM.typemap[tuple]     = Tuple
    TYPESYSTEM.typemap[set]       = Set
    TYPESYSTEM.typemap[dict]      = Dict

def typemap(typ, typesystem=TYPESYSTEM):
    try:
        if type(typ) in typesystem.__members__["universe"].values():
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

    from typed.mods.err import NotDefined
    return NotDefined

def typeof(t, typesystem=TYPESYSTEM):
    return typemap(type(t), typesystem)

def kind(x, typesystem=TYPESYSTEM):
    if any(x is a for a in typesystem.__members__["abstract"].values()):
        return "abstract"
    if any(x is u for u in typesystem.__members__["universe"].values()):
        return "universe"
    if x in typesystem.__members__["meta"]:
        return "meta"
    if x in typesystem.__members__["type"]:
        return "type"

    from typed.mods.err import NotDefined
    return NotDefined

def name(t, typesystem=TYPESYSTEM):
    """
    The 'name' polymorphism.
    """
    from typed.mods.err import NotDefined
    d = display(t)
    if d is not NotDefined:
        return d

    typ = typemap(t)

    if typ is not NotDefined:
        d = display(typ)
        if d is not NotDefined:
            return d

    from typed.mods.err import Anonymous
    return getattr(t, '__name__', Anonymous.__name__)

def term(value, type=None, typesystem=None):
    from weakref import WeakSet
    from typed.mods.err import NotDefined, TypeErr

    if typesystem is None:
        typesystem = TYPESYSTEM

    if type is None:
        type = typeof(value)

    if type is NotDefined:
        raise NotDefined(
            message="Type not defined",
            type=name(type, typesystem),
            typesystem=name(type, typesystem)
        )

    if not isterm(value, type):
        raise TypeErr(
            message="Type mismatch in term declaration",
            term=value,
            expected=type,
            received=typeof(value)
        )

    tracked = track(builtin(type))

    if tracked is not NotDefined:
        value = tracked(value)

    if not hasattr(type, "__terms__"):
        type.__terms__ = WeakSet()

    type.__terms__.add(value)

    return value

UNIVERSE = TYPESYSTEM.universe
ABSTRACT = TYPESYSTEM.abstract
