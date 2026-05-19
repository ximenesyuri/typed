from typed.mods.loader import lazy

__imports__ = {
    "typed.mods.core": [
        "__TYPESYSTEM__", "__UNIVERSE__", "__ABSTRACT__",
        "TYPESYSTEM", "UNIVERSE", "ABSTRACT",
        "typeof", "typemap",
        "new", "kind", "terms",
        "isterm", "issub", "issup",
        "name", "null"
    ]
}

if lazy(__imports__):
    from typed.mods.core import (
        __TYPESYSTEM__, __UNIVERSE__, __ABSTRACT__,
        TYPESYSTEM, UNIVERSE, ABSTRACT,
        typeof, typemap,
        new, kind, terms,
        isterm, issub, issup,
        name, null
)
