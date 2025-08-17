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
Pattern  = _Pattern("Pattern", (Str,), {})
META     = _META("Meta", (TYPE,), {})

Any.__display__     = "Any"
Pattern.__display__ = "Pattern"
META.__display__    = "META"

Condition = Typed(Any, cod=Bool)
