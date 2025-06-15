from typed.mods.factories.base import Union, Dict, Set, List, Null
from typed.mods.factories.generics import Regex
from typed.mods.helper_meta import (
    __Any,
    __Pattern,
)

Int = int
Str = str
Bool = bool
Float = float
Type = type
Nill = type(None)

Any     = __Any("Any", (), {})
Json    = Union(Dict(Any), Set(Any), List(Any))
Pattern = __Pattern("Pattern", (Str,), {})
Path    = Union(Regex(r"^/?(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?$"), Null(Str))

Any.__display__     = "Any"
Json.__display__    = "Json"
Path.__display__    = "Path"
Pattern.__display__ = "Pattern"
