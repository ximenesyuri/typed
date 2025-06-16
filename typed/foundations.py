from typed.main import typed
from typed.mods.helper.foundations import _equivalence, __CAT
from typed.mods.types.base import Type, Bool

class SET:
    """
    abstract set for all instances of typ:
    x in InstanceSet(typ) <==> isinstance(x, typ)
    """
    def __init__(self, typ):
        self.typ = typ

    def __contains__(self, x):
        return isinstance(x, self.typ)

    def __repr__(self):
        return f"SET({getattr(self.typ, '__name__', repr(self.typ))})"

    def __eq__(self, other):
        if not isinstance(other, SET):
            return NotImplemented
        return _equivalence(self.typ, other.typ)

    def __hash__(self):
        return hash((SET, id(self.typ)))

SET.__display__ = "SET"

CAT = __CAT("CAT", (), {})
CAT.__display__ = "CAT"

@typed
def equiv(X: Type, Y: Type) -> Bool:
    return SET(X) == SET(Y)

