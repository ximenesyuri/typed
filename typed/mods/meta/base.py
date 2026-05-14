from builtins import type as __Type__
from typed.mods.core import isterm, issub, TYPESYSTEM, UNIVERSE, ABSTRACT
from typed.mods.err import NotDefined

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
    """
    def __isterm__(typ, trm):
        return False

    def __issub__(typ, other):
        return True

    def __issup__(typ, other):
        return False

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "EMPTY"
    __null__ = NotDefined
    __builtin__ = NotDefined

class PARAMETRIC(TYPE):
    """
    The metatype of parametric types.
    """
    def __isterm__(typ, trm):
        from typed.mods.types.func import Factory
        from typed.mods.core import type
        if hasattr(type(trm), "__call__"):
            return type(trm).__iter__ in Factory
        return False

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "PARAMETRIC"
    __null__    = NotDefined
    __builtin__ = NotDefined

class NILL(TYPE):
    """
    The metatype of None value.
    """
    def __isterm__(typ, trm):
        return trm is None

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "NILL"
    __null__ = NotDefined
    __builtin__ = NotDefined

class ANY(TYPE):
    """
    The metatype of any value.
    """
    def __isterm__(typ, trm):
        return True

    def __issub__(typ, other):
        return False

    def __issup__(typ, other):
        return True

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "ANY"
    __null__ = NotDefined
    __builtin__ = NotDefined


class INT(TYPE):
    """
    The metatype of integers.
    """
    def __isterm__(typ, trm):
        from builtins import int as __Int__
        from typed.mods.types.base import Int
        from typed.mods.core import type, issub
        return isinstance(trm, __Int__) or issub(type(trm), Int)

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "INT"
    __null__ = NotDefined
    __builtin__ = NotDefined


class FLOAT(TYPE):
    """
    The metatype of floating-point numbers.
    """
    def __isterm__(typ, trm):
        from builtins import float as __Float__
        from typed.mods.types.base import Float
        from typed.mods.core import type, issub
        return isinstance(trm, __Float__) or issub(type(trm), Float)

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "FLOAT"
    __null__ = NotDefined
    __builtin__ = NotDefined


class STR(TYPE):
    """
    The metatype of strings.
    """
    def __isterm__(typ, trm):
        from builtins import str as __Str__
        from typed.mods.types.base import Str
        from typed.mods.core import type, issub
        return isinstance(trm, __Str__) or issub(type(trm), Str)

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "STR"
    __null__ = NotDefined
    __builtin__ = NotDefined


class BOOL(TYPE):
    """
    The metatype of booleans.
    """
    def __isterm__(typ, trm):
        from builtins import bool as __Bool__
        from typed.mods.types.base import Bool
        from typed.mods.core import type, issub
        return isinstance(trm, __Bool__) or issub(type(trm), Bool)

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "BOOL"
    __null__ = NotDefined
    __builtin__ = NotDefined


class BYTES(TYPE):
    """
    The metatype of bytes and bytearrays.
    """
    def __isterm__(typ, trm):
        from builtins import bytes as __Bytes__, bytearray as __ByteArray__
        from typed.mods.types.base import Bytes
        from typed.mods.core import type, issub
        return isinstance(trm, __Bytes__) or isinstance(trm, __ByteArray__) or issub(type(trm), Bytes)

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "BYTES"
    __null__ = NotDefined
    __builtin__ = NotDefined


class TUPLE(TYPE):
    """
    The metatype of tuples.
    """
    def __isterm__(typ, trm):
        from builtins import tuple as __Tuple__
        from typed.mods.types.base import Tuple
        from typed.mods.core import type, issub, isterm
        
        if not (isinstance(trm, __Tuple__) or issub(type(trm), Tuple)):
            return False
        
        types = getattr(typ, '__types__', None)
        if types is not None:
            for x in trm:
                if not any(isterm(x, t) for t in types):
                    return False
        return True

    def __issub__(typ, other):
        from typed.mods.core import issub
        if type(other) is type(typ):
            typ_types = getattr(typ, '__types__', None)
            other_types = getattr(other, '__types__', None)
            if typ_types is None and other_types is not None:
                return False
            if other_types is None:
                return True
            for t1 in typ_types:
                if not any(issub(t1, t2) for t2 in other_types):
                    return False
            return True
        return False

    def __call__(typ, *types, typesystem=None):
        from typed.mods.core import TYPESYSTEM, names
        if typesystem is None:
            typesystem = TYPESYSTEM
            
        types_set = set(types)
        if typesystem.is_restrictive:
            for t in types_set:
                if t not in typesystem.__types__:
                    raise TypeError(f"Type {t} not in typesystem.__types__")
                    
        name = f"Tuple({names(*types_set)})" if types_set else "Tuple()"
        
        return __Type__.__new__(typ.__class__, name, (typ,), {
            "__display__": name,
            "__types__": types_set,
            "__typesystems__": [typesystem],
            "is_type": True
        })

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "TUPLE"
    __null__ = NotDefined
    __builtin__ = NotDefined


class LIST(TYPE):
    """
    The metatype of lists.
    """
    def __isterm__(typ, trm):
        from builtins import list as __List__
        from typed.mods.types.base import List
        from typed.mods.core import type, issub, isterm
        
        if not (isinstance(trm, __List__) or issub(type(trm), List)):
            return False
            
        types = getattr(typ, '__types__', None)
        if types is not None:
            for x in trm:
                if not any(isterm(x, t) for t in types):
                    return False
        return True

    def __issub__(typ, other):
        from typed.mods.core import issub
        if type(other) is type(typ):
            typ_types = getattr(typ, '__types__', None)
            other_types = getattr(other, '__types__', None)
            if typ_types is None and other_types is not None:
                return False
            if other_types is None:
                return True
            for t1 in typ_types:
                if not any(issub(t1, t2) for t2 in other_types):
                    return False
            return True
        return False

    def __call__(typ, *types, typesystem=None):
        from typed.mods.core import TYPESYSTEM, names
        if typesystem is None:
            typesystem = TYPESYSTEM
            
        types_set = set(types)
        if typesystem.is_restrictive:
            for t in types_set:
                if t not in typesystem.__types__:
                    raise TypeError(f"Type {t} not in typesystem.__types__")
                    
        name = f"List({names(*types_set)})" if types_set else "List()"
        
        return __Type__.__new__(typ.__class__, name, (typ,), {
            "__display__": name,
            "__types__": types_set,
            "__typesystems__": [typesystem],
            "is_type": True
        })

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "LIST"
    __null__ = NotDefined
    __builtin__ = NotDefined


class SET(TYPE):
    """
    The metatype of sets.
    """
    def __isterm__(typ, trm):
        from builtins import set as __Set__
        from typed.mods.types.base import Set
        from typed.mods.core import type, issub, isterm
        
        if not (isinstance(trm, __Set__) or issub(type(trm), Set)):
            return False
            
        types = getattr(typ, '__types__', None)
        if types is not None:
            for x in trm:
                if not any(isterm(x, t) for t in types):
                    return False
        return True

    def __issub__(typ, other):
        from typed.mods.core import issub
        if type(other) is type(typ):
            typ_types = getattr(typ, '__types__', None)
            other_types = getattr(other, '__types__', None)
            if typ_types is None and other_types is not None:
                return False
            if other_types is None:
                return True
            for t1 in typ_types:
                if not any(issub(t1, t2) for t2 in other_types):
                    return False
            return True
        return False

    def __call__(typ, *types, typesystem=None):
        from typed.mods.core import TYPESYSTEM, names
        if typesystem is None:
            typesystem = TYPESYSTEM
            
        types_set = set(types)
        if typesystem.is_restrictive:
            for t in types_set:
                if t not in typesystem.__types__:
                    raise TypeError(f"Type {t} not in typesystem.__types__")
                    
        name = f"Set({names(*types_set)})" if types_set else "Set()"
        
        return __Type__.__new__(typ.__class__, name, (typ,), {
            "__display__": name,
            "__types__": types_set,
            "__typesystems__": [typesystem],
            "is_type": True
        })

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "SET"
    __null__ = NotDefined
    __builtin__ = NotDefined


class DICT(TYPE):
    """
    The metatype of dictionaries.
    """
    def __isterm__(typ, trm):
        from builtins import dict as __Dict__
        from typed.mods.types.base import Dict
        from typed.mods.core import type, issub, isterm
        
        if not (isinstance(trm, __Dict__) or issub(type(trm), Dict)):
            return False
        
        types = getattr(typ, "__types__", None)
        key_type = getattr(typ, "__key_type__", None)
        
        if types is not None:
            for v in trm.values():
                if not any(isterm(v, t) for t in types):
                    return False
                    
        if key_type is not None:
            for k in trm.keys():
                if not isterm(k, key_type):
                    return False
                    
        return True

    def __issub__(typ, other):
        from typed.mods.core import issub
        if type(other) is type(typ):
            typ_types = getattr(typ, '__types__', None)
            other_types = getattr(other, '__types__', None)
            typ_key = getattr(typ, '__key_type__', None)
            other_key = getattr(other, '__key_type__', None)
            
            if typ_types is None and other_types is not None:
                return False
            if typ_key is None and other_key is not None:
                return False
                
            if typ_types is not None and other_types is not None:
                for t1 in typ_types:
                    if not any(issub(t1, t2) for t2 in other_types):
                        return False
            
            if typ_key is not None and other_key is not None:
                if not issub(typ_key, other_key):
                    return False
                    
            return True
        return False

    def __call__(typ, *types, key=None, typesystem=None):
        from typed.mods.core import TYPESYSTEM, names, name
        if typesystem is None:
            typesystem = TYPESYSTEM
        
        types_set = set(types)
        if typesystem.is_restrictive:
            for t in types_set:
                if t not in typesystem.__types__:
                    raise TypeError(f"Type {t} not in typesystem.__types__")
            if key is not None and key not in typesystem.__types__:
                raise TypeError(f"Type {key} not in typesystem.__types__")
        
        if key is not None:
            display_name = f"Dict({names(*types_set)}, key={name(key)})" if types_set else f"Dict(key={name(key)})"
        else:
            display_name = f"Dict({names(*types_set)})" if types_set else "Dict()"
            
        return __Type__.__new__(typ.__class__, display_name, (typ,), {
            "__display__": display_name,
            "__types__": types_set,
            "__key_type__": key,
            "__typesystems__": [typesystem],
            "is_type": True
        })

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "DICT"
    __null__ = NotDefined
    __builtin__ = NotDefined


TYPESYSTEM.add(
    EMPTY, PARAMETRIC, ANY,
    NILL, INT, FLOAT, STR, BOOL, BYTES,
    TUPLE, LIST, SET, DICT
)
