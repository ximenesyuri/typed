from typed.mods.factories.base import Union, Dict, Set, List

Int = int
Str = str
Bool = bool
Float = float

class Any(type):
    def __instancecheck__(cls, instance):
        return True

Json = Union(Dict(Str, Any), Set(Any), List(Any))
