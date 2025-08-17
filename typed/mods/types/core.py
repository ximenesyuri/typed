from typed.mods.factories.base import Union, Dict, Set, List
from typed.mods.factories.generics import Regex, Null
from typed.mods.types.base import Any, Str

Path = Union(Regex(r"^/?(?:(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?|/?)$"), Null(Str))
Json = Union(Dict(Any), Set(Any), List(Any))

Json.__display__  = "Json"
Path.__display__  = "Path"
