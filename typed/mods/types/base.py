from typed.mods.meta.base import (
    _TYPE_, _META_, _DISCOURSE_, _PARAMETRIC_,
    NILL, ANY,
    STR, INT, FLOAT, BOOL,
    TUPLE, LIST, SET, DICT,
)

Nill  = NILL("Nill", (), {"__display__": "Nill", "__null__": None})
TYPE  = _TYPE_("TYPE", (), {
    "__display__": "TYPE",
    "__null__": Nill
})
META = _META_("META", (TYPE,), {
    "__display__": "META",
    "__null__": NILL
})
DISCOURSE = _DISCOURSE_("DISCOURSE", (TYPE,), {
    "__display__": "DISCOURSE",
    "__null__": NILL
})
PARAMETRIC = _PARAMETRIC_("PARAMETRIC", (TYPE,), {
    "__display__": "PARAMETRIC",
    "__null__": NILL
})

Nill  = NILL("Nill", (), {"__display__": "Nill", "__null__": None})
Int   = INT("Int", (), {"__display__": "Int", "__null__": 0})
Float = FLOAT("Int", (), {"__display__": "Float", "__null__": 0.0})
Bool  = BOOL("Bool", (), {"__display__": "Bool", "__null__": False})
Str   = STR("Str", (), {"__display__": "Str", "__null__": ""})
Any   = ANY("Any", (), {"__display__": "Any", "__null__": None})

Tuple = TUPLE("Tuple", (), {"__display__": "Tuple", "__null__": ()})
List  = LIST("List", (), {"__display__": "List", "__null__": []})
Set   = SET("Set", (), {"__display__": "Set", "__null__": set()})
Dict  = DICT("Dict", (), {"__display__": "Dict", "__null__": {}})
