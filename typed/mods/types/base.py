from typed.mods.factories.base import Union, Dict, Set, List, Null
from typed.mods.factories.generics import Regex, Enum
from typed.mods.types.meta import (
    _Any,
    _Pattern,
    _META,
)
from typed.mods.types.func import Typed

Int   = int
Str   = str
Bool  = bool
Float = float
TYPE  = type
Nill  = type(None)

class Empty: pass

Any      = _Any("Any", (), {})
Json     = Union(Dict(Any), Set(Any), List(Any))
Pattern  = _Pattern("Pattern", (Str,), {})
Path     = Union(Regex(r"^/?(?:(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?|/?)$"), Null(Str))
Protocol = Enum(Str, "http", "https", "file", "ftp")
META     = _META("Meta", (TYPE,), {})

Any.__display__     = "Any"
Json.__display__    = "Json"
Path.__display__    = "Path"
Pattern.__display__ = "Pattern"
META.__display__    = "META"

Condition = Typed(Any, cod=Bool)
