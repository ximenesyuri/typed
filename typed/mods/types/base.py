from typed.mods.factories.base import Union, Dict, Set, List
from typed.mods.factories.generics import Regex

Int   = int
Str   = str
Bool  = bool
Float = float
Type  = type
Nill  = type(None)

class _AnyMeta(type):
    def __instancecheck__(cls, instance):
        return True
    def __subclasscheck__(cls, subclass):
        return True
Any = _AnyMeta("Any", (), {})

Json = Union(Dict(Any), Set(Any), List(Any))
Path = Regex(r"^/?(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?$")
