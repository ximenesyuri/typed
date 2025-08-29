from typed.mods.meta.base import (
    _TYPE_,
    NILL,
    ANY,
    PATTERN,
    _META_,
    _ITER_,
    STR,
    INT,
    FLOAT,
    BOOL,
    TUPLE,
    LIST,
    SET,
    DICT
)

class Empty: pass
class EMPTY(type): pass

TYPE  = _TYPE_("TYPE", (type,), {"__display__": "TYPE", "__null__": Empty})
Nill  = NILL("Nill", (), {"__display__": "Nill", "__null__": None})
Int   = INT("Int", (), {"__display__": "Int", "__null__": 0})
Float = FLOAT("Int", (), {"__display__": "Float", "__null__": 0.0})
Bool  = BOOL("Bool", (), {"__display__": "Bool", "__null__": False})
Str   = STR("Str", (), {"__display__": "Str", "__null__": ""})

Any      = ANY("Any", (), {"__display__": "Any", "__null__": None})
Pattern  = PATTERN("Pattern", (Str,), {"__display__": "Pattern", "__null__": ""})
META     = _META_("META", (TYPE,), {"__display__": "META", "__null__": EMPTY})
ITER     = _TYPE_("ITER", (TYPE,), {"__display__": "META", "__null__": EMPTY})

Tuple = TUPLE("Tuple", (), {"__display__": "Tuple", "__null__": ()})
List  = LIST("List", (), {"__display__": "List", "__null__": []})
Set   = SET("Set", (), {"__display__": "Set", "__null__": set()})
Dict  = DICT("Dict", (), {"__display__": "Dict", "__null__": {}})
