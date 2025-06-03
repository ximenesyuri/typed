from typed.mods.helper import __Any
from typed.mods.factories.base import Union, Dict, Set, List, Null
from typed.mods.factories.generics import Regex

Int   = int
Str   = str
Bool  = bool
Float = float
Type  = type
Nill  = type(None)

Any   = __Any("Any", (), {})
Json = Union(Dict(Any), Set(Any), List(Any))
Path = Union(Regex(r"^/?(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?$"), Null(Str))

Any.__display__   = "Any"
Json.__display__  = "Json"
Path.__display__  = "Path"
