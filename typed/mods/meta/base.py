from typed.mods.core import term, sub, TYPESYSTEM

def UNIVERSE(level, typesystem=TYPESYSTEM):
    if level < 0:
        return typesystem.universe

    typesystem.populate(level=level+1)
    return typesystem.__universes__[level]

def ABSTRACT(level, typesystem=TYPESYSTEM):
    if level < 0:
        return typesystem.abstract

    typesystem.populate(level=level+1)
    return typesystem.__abstracts__[level]

TYPE = UNIVERSE(0)
META = ABSTRACT(0)

print(TYPE in META)

class PARAMETRIC(TYPE):
    def __term__(typ, trm):
        from typed.mods.types.func import Factory
        from typed.mods.core import type
        if hasattr(type(trm), "__call__"):
            return type(trm).__iter__ in Factory
        return False

class EMPTY(TYPE):
    def __term__(typ, trm):
        return False

class NILL(TYPE):
    def __term__(typ, trm):
        return trm is None

class ANY(TYPE):
    def __term__(typ, trm):
        return True
    def __sub__(typ, other):
        return True

class INT(TYPE):
    def __term__(typ, trm):
        from builtins import int as __Int__
        from typed.mods.types.base import Int
        from typed.mods.core import type
        return term(trm, __Int__) or sub(type(trm), Int)

class FLOAT(TYPE):
    def __term__(typ, trm):
        from builtins import float as __Float__
        from typed.mods.types.base import Float
        from typed.mods.core import type
        return term(trm, __Float__) or sub(type(trm), Float)

class STR(TYPE):
    def __term__(typ, trm):
        from builtins import str as __Str__
        from typed.mods.types.base import Str
        from typed.mods.core import type
        return term(trm, __Str__) or sub(type(trm), Str)

class BOOL(TYPE):
    def __term__(typ, trm):
        from builtins import bool as __Bool__
        from typed.mods.types.base import Bool
        from typed.mods.core import type
        return term(trm, __Bool__) or sub(type(trm), Bool)

class BYTES(TYPE):
    def __term__(typ, trm):
        from builtins import bytes as __Bytes__, bytearray as __ByteArray__
        from typed.mods.types.base import Bytes
        from typed.mods.core import type
        return term(trm, __Bytes__) or term(trm, __ByteArray__) or sub(type(trm), Bytes)

class TUPLE(TYPE):
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

class LIST(TYPE):
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

class SET(TYPE):
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

class DICT(TYPE):
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

class PATTERN(STR):
    def __term__(typ, trm):
        import re
        from typed.mods.types.base import Str
        if not term(trm, Str):
            return False
        try:
            re.compile(trm)
            return True
        except re.error:
            return False

class CONTAINER(TYPE):
    def __term__(typ, trm):
        if hasattr(type(trm), "__contains__"):
            return True
        return False
