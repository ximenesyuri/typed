from typed.mods.factories.base import Union, Dict, Set, List, Null
from typed.mods.factories.generics import Regex
from typed.mods.helper.helper import (
    _Any,
    _Pattern,
)

Int   = int
Str   = str
Bool  = bool
Float = float
Type  = type
Nill  = type(None)

Any     = _Any("Any", (), {})
Json    = Union(Dict(Any), Set(Any), List(Any))
Pattern = _Pattern("Pattern", (Str,), {})
Path    = Union(Regex(r"^/?(?:(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?|/?)$"), Null(Str))

Any.__display__     = "Any"
Json.__display__    = "Json"
Path.__display__    = "Path"
Pattern.__display__ = "Pattern"
