from typed.mods.meta.base import (
    TYPESYSTEM,
    EMPTY, NILL, ANY,
    TYPE, PARAMETRIC,
    STR, INT, FLOAT, BOOL, BYTES,
    TUPLE, LIST, SET, DICT,
    PATTERN, CONTAINER
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

class Empty(metaclass=EMPTY):
    """
    The type with no terms.

    > type(Empty)    is EMPTY
    > term(x, Empty) is always False
    > sub(T, Empty)  is True iff T is Empty
    > null(Empty)    is NotDefined
    """
    __typesystem__ = TYPESYSTEM
    __type__       = EMPTY
    __display__    = "Empty"

class Nill(metaclass=NILL):
    """
    The type with None value.

    > type(Nill)    is NILL
    > term(x, Nill) is True iff x is None
    > null(Nill)    is None
    > builtin(Nill) is NotDefined
    """
    __typesystem__ = TYPESYSTEM
    __type__       = NILL
    __display__    = "Nill"
    __null__       = None

class Any(metaclass=ANY):
    """
    The type of anything.

    > type(Any)     is ANY
    > term(x, Any)  is always True
    > null(Any)     is None
    > builtin(Any)  is NotDefined
    """
    __typesystem__ = TYPESYSTEM
    __type__       = ANY
    __display__    = "Any"
    __null__       = None

Cls  = Any
Self = Any

class Type(metaclass=TYPE):
    """
    The type of all non-universe types.

    > type(Type)    is TYPE
    > term(x, Type) is True iff
    > null(Type)    is Nill
    > builtin(Type) is type
    """
    __typesystem__ = TYPESYSTEM
    __type__       = TYPE
    __display__    = "Type"
    __null__       = Nill
    __builtin__    = __Type__

class Parametric(metaclass=PARAMETRIC):
    """
    The type of parametric types.

    > type(Parametric) is PARAMETRIC
    > null(Parametric) is Nill

    """
    __typesystem__ = TYPESYSTEM
    __type__       = PARAMETRIC
    __display__    = "Parametric"
    __null__       = Nill

class Int(metaclass=INT):
    """
    The type of integers.

    > type(Int)    is INT
    > null(Int)    is 0
    > builtin(Int) is int
    """
    __typesystem__ = TYPESYSTEM
    __type__       = INT
    __display__    = "Int"
    __null__       = 0
    __builtin__    = __Int__

class Float(metaclass=FLOAT):
    """
    The type of floats.

    > type(Float)    is FLOAT
    > null(Float)    is 0.0
    > builtin(Float) is float
    """
    __typesystem__ = TYPESYSTEM
    __type__       = FLOAT
    __display__    = "Float"
    __null__       = 0.0
    __builtin__    = __Float__

class Bool(metaclass=BOOL):
    """
    The type of booleans.

    > type(Bool)    is BOOL
    > null(Bool)    is False
    > builtin(Bool) is bool
    """
    __typesystem__ = TYPESYSTEM
    __type__       = BOOL
    __display__    = "Bool"
    __null__       = False
    __builtin__    = __Bool__

class Str(metaclass=STR):
    """
    The type of strings.

    > type(Str)    is STR
    > null(Str)    is ""
    > builtin(Str) is str
    """
    def __len__(self, obj):
        return len(obj)

    __typesystem__ = TYPESYSTEM
    __type__       = STR
    __display__    = "Str"
    __null__       = ""
    __builtin__    = __Str__

class Bytes(metaclass=BYTES):
    """
    The type of bytes.

    > type(Bytes)  is BYTES
    > null(Bytes)  is bytes()
    > builtin(Str) is bytes
    """

    __typesystem__ = TYPESYSTEM
    __type__       = BYTES
    __display__    = "Bytes"
    __null__       = __Bytes__()
    __builtin__    = __Bytes__


class Tuple(metaclass=TUPLE):
    """
    The parametric type of tuples.

    > type(Tuple)    is TUPLE
    > null(Tuple)    is tuple()
    > builtin(Tuple) is tuple
    """
    __typesystem__ = TYPESYSTEM
    __type__       = TUPLE
    __display__    = "Tuple"
    __null__       = tuple()
    __builtin__    = __Tuple__


class List(metaclass=LIST):
    """
    The parametric type of lists.

    > type(List)    is LIST
    > null(List)    is []
    > builtin(List) is list
    """
    __typesystem__ = TYPESYSTEM
    __type__       = LIST
    __display__    = "List"
    __null__       = []
    __builtin__    = __List__


class Set(metaclass=SET):
    """
    The parametric type of sets.

    > type(Set)    is SET
    > null(Set)    is set()
    > builtin(Set) is set
    """
    __typesystem__ = TYPESYSTEM
    __type__       = SET
    __display__    = "Set"
    __null__       = __Set__()
    __builtin__    = __Set__

class Dict(metaclass=DICT):
    """
    The parametric type of dicts.

    > type(Dict)    is DICT
    > null(Dict)    is {}
    > builtin(Dict) is dict
    """
    __display__ = "Dict"
    __null__    = {}
    __builtin__ = __Dict__

    def __getitem__(trm, key):
        return trm.__dict__[key]
    def __setitem__(trm, key, value):
        trm.__dict__[key] = value
    def __contains__(trm, key):
        return key in trm.__dict__

Pattern = PATTERN("Pattern", (Str,), {"__display__": "Pattern", "__null__": ""})
Container = CONTAINER("Container", (List, Tuple, Set), {"__display__": "Container", "__null__": []})
