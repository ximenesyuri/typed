from typed.mods.meta.base import (
    TYPESYSTEM,
    EMPTY, NILL, ANY,
    TYPE, PARAMETRIC,
    STR, INT, FLOAT, BOOL, BYTES,
    TUPLE, LIST, SET, DICT,
)
from builtins import (
    type  as __Type__,
    int   as __Int__,
    float as __Float__,
    bool  as __Bool__,
    str   as __Str__,
    tuple as __Tuple__,
    set   as __Set__,
    list  as __List__,
    dict  as __Dict__,
    bytes as __Bytes__
)
from typed.mods.err import NotDefined

class Empty(metaclass=EMPTY):
    """
    The type with no terms.

    : type(Empty)    is  EMPTY
    : isterm(x, Empty) :=  False
    : issub(T, Empty)  iff T is Empty
    : null(Empty)    is  NotDefined
    : builtin(Empty) is  NotDefined
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = EMPTY
    __display__    = "Empty"
    __null__       = NotDefined
    __builtin__    = NotDefined

class Nill(metaclass=NILL):
    """
    The type with None value.

    : type(Nill)    is  NILL
    : isterm(x, Nill) iff x is None
    : null(Nill)    is  None
    : builtin(Nill) is  NotDefined
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = NILL
    __display__    = "Nill"
    __null__       = None

class Any(metaclass=ANY):
    """
    The type of anything.

    : type(Any)     is ANY
    : isterm(x, Any)  := True
    : null(Any)     is None
    : builtin(Any)  is NotDefined
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = ANY
    __display__    = "Any"
    __null__       = None
    __builtin__    = NotDefined

class Type(metaclass=TYPE):
    """
    The type of all non-universe types.

    : type(Type)    is  TYPE := UNIVERSE(0)
    : isterm(x, Type) iff issub(type(x), Type)
    : null(Type)    is  Nill
    : builtin(Type) is  type
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = TYPE
    __display__    = "Type"
    __null__       = Nill
    __builtin__    = __Type__

class Parametric(metaclass=PARAMETRIC):
    """
    The type of parametric types.

    : type(Parametric) is PARAMETRIC
    : null(Parametric) is NotDefined
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = PARAMETRIC
    __display__    = "Parametric"
    __null__       = Nill

class Int(metaclass=INT):
    """
    The type of integers.

    : type(Int)    is INT
    : null(Int)    is 0
    : builtin(Int) is int
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = INT
    __display__    = "Int"
    __null__       = 0
    __builtin__    = __Int__

class Float(metaclass=FLOAT):
    """
    The type of floats.

    : type(Float)    is FLOAT
    : null(Float)    is 0.0
    : builtin(Float) is float
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = FLOAT
    __display__    = "Float"
    __null__       = 0.0
    __builtin__    = __Float__

class Bool(metaclass=BOOL):
    """
    The type of booleans.

    : type(Bool)    is BOOL
    : null(Bool)    is False
    : builtin(Bool) is bool
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = BOOL
    __display__    = "Bool"
    __null__       = False
    __builtin__    = __Bool__

class Str(metaclass=STR):
    """
    The type of strings.

    : type(Str)    is STR
    : null(Str)    is ""
    : builtin(Str) is str
    """
    def __len__(self, obj):
        return len(obj)

    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = STR
    __display__    = "Str"
    __null__       = ""
    __builtin__    = __Str__

class Bytes(metaclass=BYTES):
    """
    The type of bytes.

    : type(Bytes)  is BYTES
    : null(Bytes)  is bytes()
    : builtin(Str) is bytes
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = BYTES
    __display__    = "Bytes"
    __null__       = __Bytes__()
    __builtin__    = __Bytes__


class Tuple(metaclass=TUPLE):
    """
    The parametric type of tuples.

    : type(Tuple)    is TUPLE
    : null(Tuple)    is tuple()
    : builtin(Tuple) is tuple
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = TUPLE
    __display__    = "Tuple"
    __null__       = tuple()
    __builtin__    = __Tuple__


class List(metaclass=LIST):
    """
    The parametric type of lists.

    : type(List)    is LIST
    : null(List)    is []
    : builtin(List) is list
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = LIST
    __display__    = "List"
    __null__       = []
    __builtin__    = __List__


class Set(metaclass=SET):
    """
    The parametric type of sets.

    : type(Set)    is SET
    : null(Set)    is set()
    : builtin(Set) is set
    """
    is_type        = True
    __typesystems__ = [TYPESYSTEM]
    __type__       = SET
    __display__    = "Set"
    __null__       = __Set__()
    __builtin__    = __Set__

class Dict(metaclass=DICT):
    """
    The parametric type of dicts.

    : type(Dict)    is DICT
    : null(Dict)    is {}
    : builtin(Dict) is dict
    """
    is_type     = True
    __typesystems__ = [TYPESYSTEM]
    __display__ = "Dict"
    __null__    = {}
    __builtin__ = __Dict__

    def __getitem__(trm, key):
        return trm.__dict__[key]
    def __setitem__(trm, key, value):
        trm.__dict__[key] = value
    def __contains__(trm, key):
        return key in trm.__dict__

TYPESYSTEM.add(
    Type,
    Empty, Nill, Any,
    Int, Float, Str, Bool, Bytes,
    List, Tuple, Set, Dict    
)
