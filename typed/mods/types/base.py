from typed.mods.types.meta import (
    _TYPE,
    _Nill,
    _Any,
    _Pattern,
    _META,
    _Str,
    _Int,
    _Float,
    _Bool
)
from typed.mods.types.func import Typed

class Empty: pass
class EMPTY(type): pass

TYPE  = _TYPE("TYPE", (type,), {"__display__": "TYPE", "__null__": Empty})
Nill  = _Nill("Nill", (), {"__display__": "Nill", "__null__": None})
Int   = _Int("Int", (int,), {"__display__": "Int", "__null__": 0})
Float = _Float("Int", (float,), {"__display__": "Float", "__null__": 0.0})
Bool  = _Bool("Bool", (), {"__display__": "Bool", "__null__": False})
Str   = _Str("Str", (str,), {"__display__": "Str", "__null__": ""})

Any      = _Any("Any", (), {"__display__": "Any", "__null__": None})
Pattern  = _Pattern("Pattern", (Str,), {"__display__": "Pattern", "__null__": ""})
META     = _META("META", (TYPE,), {"__display__": "META", "__null__": EMPTY})

Condition = Typed(Any, cod=Bool)
