from builtins import type as __Type__
from typed.mods.core import term, sub, TYPESYSTEM
from typed.mods.err import NotDefined

__UNIVERSE__ = TYPESYSTEM.universe
__UNIVERSE__.__typesystem__ = TYPESYSTEM
__UNIVERSE__.__type__ = __Type__

__ABSTRACT__ = TYPESYSTEM.abstract
__ABSTRACT__.__typesystem__ = TYPESYSTEM
__ABSTRACT__.__type__ = __Type__

def UNIVERSE(n: int, typesystem=TYPESYSTEM) -> __Type__:
    """
    The universe hyerarchy factory.

    : n: int
    : typesystem: typesystem

    : type(UNIVERSE(n, typesystem))    is UNIVERSE(n+1, typesystem)
    : term(T, UNIVERSE(n, typesystem)) iff sub(type(T), UNIVERSE(n, typesystem))
    : null(T, UNIVERSE(n, typesystem)) is NotDefined
    : builtin(UNIVERSE(n, typesystem)) is NotDefined
    """

    if n < 0:
        return typesystem.universe

    typesystem.populate(level=n+1)
    UNI = typesystem.__universes__[n]
    UNI.__typesystem__ = typesystem
    UNI.__type__ = typesystem.__universes__[n+1]
    UNI.__builtin__ = NotDefined
    UNI.__null__ = NotDefined
    return UNI

def ABSTRACT(n: int, typesystem=TYPESYSTEM) -> __Type__:
    """
    The abstracts (universe subtypes) hyerarchy factory

    : n: int
    : typesystem: typesystem

    : type(ABSTRACT(n, typesystem))    is UNIVERSE(n, typesystem)
    : term(T, ABSTRACT(n, typesystem)) iff sub(T, UNIVERSE(n, typesystem))
    : null(T, ABSTRACT(n, typesystem)) is NotDefined
    : builtin(ABSTRACT(n, typesystem)) is  NotDefined
    """

    if n < 0:
        return typesystem.abstract

    typesystem.populate(level=n+1)
    ABS = typesystem.__abstracts__[n]
    ABS.__typesystem__ = typesystem
    ABS.__type__ = typesystem.__universes__[n+1]
    ABS.__builtin__ = NotDefined
    ABS.__null__ = NotDefined
    return ABS

TYPE = UNIVERSE(0)
TYPE.__name__ = "TYPE"
TYPE.__display__ = TYPE.__name__
TYPE.__builtin__ = NotDefined

META = ABSTRACT(0)
META.__name__ = "TYPE"
META.__display__ = META.__name__
META.__builtin__ = NotDefined

class EMPTY(TYPE):
    """
    The metatype of nothing.

    : type(EMPTY)    is UNIVERSE(1)
    : term(T, EMPTY) iff sub(type(T), EMPTY)
    : null(EMPTY)    is NotDefined
    : builtin(EMPTY) is NotDefined
    """
    def __term__(typ, trm):
        return False

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "EMPTY"
    __null__ = NotDefined
    __builtin__ = NotDefined

class PARAMETRIC(TYPE):
    """
    The metatype of parametric types.

    : type(PARAMETRIC)    is UNIVERSE(1)
    : term(T, PARAMETRIC) iff sub(type(T), PARAMETRIC)
    : null(PARAMETRIC)    is NotDefined
    : builtin(PARAMETRIC) is NotDefined
    """
    def __term__(typ, trm):
        from typed.mods.types.func import Factory
        from typed.mods.core import type
        if hasattr(type(trm), "__call__"):
            return type(trm).__iter__ in Factory
        return False

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "PARAMETRIC"
    __null__    = NotDefined
    __builtin__ = NotDefined

class NILL(TYPE):
    """
    The metatype of None value.

    : type(NILL)    is UNIVERSE(1)
    : term(T, NILL) iff sub(type(T), NILL)
    : null(NILL)    is NotDefined
    : builtin(NILL) is NotDefined
    """

    def __term__(typ, trm):
        return trm is None

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "NILL"
    __null__ = NotDefined
    __builtin__ = NotDefined

class ANY(TYPE):
    """
    The metatype of any value.

    : type(ANY)    is UNIVERSE(1)
    : term(T, ANY) iff sub(type(T), ANY)
    : null(ANY)    is NotDefined
    : builtin(ANY) is NotDefined
    """
    def __term__(typ, trm):
        return True
        
    def __sub__(typ, other):
        return True

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "ANY"
    __null__ = NotDefined
    __builtin__ = NotDefined


class INT(TYPE):
    """
    The metatype of integers.

    : type(INT)    is UNIVERSE(1)
    : term(T, INT) iff sub(type(T), INT)
    : null(INT)    is NotDefined
    : builtin(INT) is NotDefined
    """
    def __term__(typ, trm):
        from builtins import int as __Int__
        from typed.mods.types.base import Int
        from typed.mods.core import type
        return term(trm, __Int__) or sub(type(trm), Int)

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "INT"
    __null__ = NotDefined
    __builtin__ = NotDefined


class FLOAT(TYPE):
    """
    The metatype of floating-point numbers.

    : type(FLOAT)    is UNIVERSE(1)
    : term(T, FLOAT) iff sub(type(T), FLOAT)
    : null(FLOAT)    is NotDefined
    : builtin(FLOAT) is NotDefined
    """
    def __term__(typ, trm):
        from builtins import float as __Float__
        from typed.mods.types.base import Float
        from typed.mods.core import type
        return term(trm, __Float__) or sub(type(trm), Float)

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "FLOAT"
    __null__ = NotDefined
    __builtin__ = NotDefined


class STR(TYPE):
    """
    The metatype of strings.

    : type(STR)    is UNIVERSE(1)
    : term(T, STR) iff sub(type(T), STR)
    : null(STR)    is NotDefined
    : builtin(STR) is NotDefined
    """
    def __term__(typ, trm):
        from builtins import str as __Str__
        from typed.mods.types.base import Str
        from typed.mods.core import type
        return term(trm, __Str__) or sub(type(trm), Str)

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "STR"
    __null__ = NotDefined
    __builtin__ = NotDefined


class BOOL(TYPE):
    """
    The metatype of booleans.

    : type(BOOL)    is UNIVERSE(1)
    : term(T, BOOL) iff sub(type(T), BOOL)
    : null(BOOL)    is NotDefined
    : builtin(BOOL) is NotDefined
    """
    def __term__(typ, trm):
        from builtins import bool as __Bool__
        from typed.mods.types.base import Bool
        from typed.mods.core import type
        return term(trm, __Bool__) or sub(type(trm), Bool)

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "BOOL"
    __null__ = NotDefined
    __builtin__ = NotDefined


class BYTES(TYPE):
    """
    The metatype of bytes and bytearrays.

    : type(BYTES)    is UNIVERSE(1)
    : term(T, BYTES) iff sub(type(T), BYTES)
    : null(BYTES)    is NotDefined
    : builtin(BYTES) is NotDefined
    """
    def __term__(typ, trm):
        from builtins import bytes as __Bytes__, bytearray as __ByteArray__
        from typed.mods.types.base import Bytes
        from typed.mods.core import type
        return term(trm, __Bytes__) or term(trm, __ByteArray__) or sub(type(trm), Bytes)

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "BYTES"
    __null__ = NotDefined
    __builtin__ = NotDefined


class TUPLE(TYPE):
    """
    The metatype of tuples.

    : type(TUPLE)    is UNIVERSE(1)
    : term(T, TUPLE) iff sub(type(T), TUPLE)
    : null(TUPLE)    is NotDefined
    : builtin(TUPLE) is NotDefined
    """
    def __term__(typ, trm):
        from builtins import tuple as __Tuple__
        from typed.mods.types.base import Tuple
        from typed.mods.core import type
        if not term(trm, __Tuple__) and not sub(type(trm), Tuple):
            return False
        types = getattr(typ, '__types__', None)
        if types is not None:
            return all(term(x, types[i]) for x, i in enumerate(trm))
        return True

    def __sub__(typ, other):
        from typed.mods.types.base import Any, Tuple
        types = getattr(typ, '__types__', None)
        if types is None:
            return sub(typ, other)

        if hasattr(other, '__bases__') and (Tuple in other.__bases__) and hasattr(other, '__types__'):
            other_element_types = other.__types__
            return all(any(sub(st, ct) for ct in typ.__types__) for st in other_element_types)
        return False

    def __call__(type, *args, **kwargs):
        from typed.mods.parametric.base import _Tuple_
        return _Tuple_(*args, **kwargs)

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "TUPLE"
    __null__ = NotDefined
    __builtin__ = NotDefined


class LIST(TYPE):
    """
    The metatype of lists.

    : type(LIST)    is UNIVERSE(1)
    : term(T, LIST) iff sub(type(T), LIST)
    : null(LIST)    is NotDefined
    : builtin(LIST) is NotDefined
    """
    def __term__(typ, trm):
        from builtins import list as __List__
        from typed.mods.types.base import List
        from typed.mods.core import type
        if not term(trm, __List__) and not sub(type(trm), List):
            return False
        types = getattr(typ, '__types__', None)
        if types is not None:
            return all(term(x, types[i]) for x, i in enumerate(trm))
        return True

    def __sub__(typ, other):
        from typed.mods.types.base import List
        if hasattr(other, '__bases__') and List in other.__bases__ and hasattr(other, '__types__'):
            other_element_types = other.__types__
            return all(any(sub(st, ct) for ct in typ.__types__) for st in other_element_types)
        return False

    def __call__(type, *args, **kwargs):
        from typed.mods.parametric.base import _List_
        return _List_(*args, **kwargs)

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "LIST"
    __null__ = NotDefined
    __builtin__ = NotDefined


class SET(TYPE):
    """
    The metatype of sets.

    : type(SET)    is UNIVERSE(1)
    : term(T, SET) iff sub(type(T), SET)
    : null(SET)    is NotDefined
    : builtin(SET) is NotDefined
    """
    def __term__(typ, trm):
        from builtins import set as __Set__
        from typed.mods.types.base import Set
        from typed.mods.core import type
        if not term(trm, __Set__) and not sub(type(trm), Set):
            return False
        from typed.mods.types.base import Any
        if Any is typ.__bases__:
            return True
        if hasattr(type, "__types__"):
            return all(term(x, _inner_union(type.__types__)) for x in trm)
        return True

    def __sub__(typ, other):
        from typed.mods.types.base import Any, Set
        if other is typ or other is Any or sub(other, Set):
            return True
        if hasattr(other, '__bases__') and Set in other.__bases__ and hasattr(other, '__types__'):
            other_element_types = other.__types__
            return all(any(sub(st, ct) for ct in typ.__types__) for st in other_element_types)
        return False

    def __call__(type, *args, **kwargs):
        from typed.mods.parametric.base import _Set_
        return _Set_(*args, **kwargs)

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "SET"
    __null__ = NotDefined
    __builtin__ = NotDefined


class DICT(TYPE):
    """
    The metatype of dictionaries.

    : type(DICT)    is UNIVERSE(1)
    : term(T, DICT) iff sub(type(T), DICT)
    : null(DICT)    is NotDefined
    : builtin(DICT) is NotDefined
    """
    def __term__(typ, trm):
        from builtins import dict as __Dict__
        from typed.mods.types.base import Dict
        from typed.mods.core import type
        if not term(trm, __Dict__) and not sub(type(trm), Dict):
            return False
        if hasattr(typ, "__types__"):
            if not all(term(v, _inner_dict_union(type.__types__)) for v in trm.values()):
                return False
        if hasattr(typ, "__key_type__"):
            if typ.__key_type__ is not None:
                if not all(term(k, typ.__key_type__) for k in trm.keys()):
                    return False
        return True

    def __sub__(typ, other):
        from typed.mods.types.base import Any, Dict
        if other is typ or other is Any or sub(other, Dict):
            return True
        if hasattr(other, '__bases__') and Dict in other.__bases__ and hasattr(other, '__types__'):
            other_value_union_types = other.__types__
            keys_match = True
            if hasattr(other, '__key_type__') and typ.__key_type__ is not None:
                keys_match = sub(getattr(other, '__key_type__'), typ.__key_type__)
            return (
                all(any(sub(svt, vt) for vt in typ.__types__) for svt in other_value_union_types)
                and keys_match
            )
        return False

    def __call__(type, *args, **kwargs):
        from typed.mods.parametric.base import _Dict_
        return _Dict_(*args, **kwargs)

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "DICT"
    __null__ = NotDefined
    __builtin__ = NotDefined
