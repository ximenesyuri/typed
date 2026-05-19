from typed.mods.loader import lazy

__imports__ = {
    "typed.mods.err": [
        "notify", "Err",
        "FuncErr", "HintErr",
        "TypeErr", "CodErr", "DomErr",
        "TypeSystemErr",
        "NotDefined", "Anonymous"
    ]
}

if lazy(__imports__):
    from typed.mods.err import (
        notify, Err,
        FuncErr, HintErr,
        TypeErr, CodErr, DomErr,
        TypeSystemErr,
        NotDefined, Anonymous
    )
