from typed.mods.meta.base import (
    _TYPE_,
    NILL,
    ANY,
    PATTERN,
    _META_,
    STR,
    INT,
    FLOAT,
    BOOL
)

class Empty: pass
class EMPTY(type): pass

TYPE  = _TYPE_("TYPE", (type,), {"__display__": "TYPE", "__null__": Empty})
Nill  = NILL("Nill", (), {"__display__": "Nill", "__null__": None})
Int   = INT("Int", (int,), {"__display__": "Int", "__null__": 0})
Float = FLOAT("Int", (float,), {"__display__": "Float", "__null__": 0.0})
Bool  = BOOL("Bool", (), {"__display__": "Bool", "__null__": False})

class Str(str, metaclass=STR):
    def __join__(*args):
        return ''.join(args)

    __display__="Str"
    __null__=""

Any      = ANY("Any", (), {"__display__": "Any", "__null__": None})
Pattern  = PATTERN("Pattern", (Str,), {"__display__": "Pattern", "__null__": ""})
META     = _META_("META", (TYPE,), {"__display__": "META", "__null__": EMPTY})
