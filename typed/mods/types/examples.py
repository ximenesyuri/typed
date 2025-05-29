from typed.mods.factories import Union, Dict, Set, List, Str

class Any(type):
    def __instancecheck__(cls, instance):
        return True

Json = Union(Dict(Str, Any), Set(Any), List(Any))
