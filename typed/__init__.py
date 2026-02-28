from importlib import import_module as __import__
from typing import TYPE_CHECKING as __lsp__

__all__ = [
    "typed",

    "Union", "Prod", "Inter", "Filter", "Compl", "Regex", "Interval",
    "Range", "Not", "Enum", "Single", "Null", "Len", "Maybe",

    "model", "value", "validate",

    "Nill", "Any",
    "Int", "Str", "Float", "Bool", "Bytes", "Self", "Cls",
    "Tuple", "List", "Set", "Dict", "Pattern",

    "Function", "Hinted", "Typed", "TYPE",

    "name", "names", "null", "new", "_", "var", "append", "switch", "func"
]

__lazy__ = {
    "typed":     ("typed.mods.decorators", "typed"),

    "Union":     ("typed.mods.factories.base", "Union"),
    "Prod":      ("typed.mods.factories.base", "Prod"),
    "Inter":     ("typed.mods.factories.generics", "Inter"),
    "Filter":    ("typed.mods.factories.generics", "Filter"),
    "Compl":     ("typed.mods.factories.generics", "Compl"),
    "Regex":     ("typed.mods.factories.generics", "Regex"),
    "Interval":  ("typed.mods.factories.generics", "Interval"),
    "Range":     ("typed.mods.factories.generics", "Range"),
    "Not":       ("typed.mods.factories.generics", "Not"),
    "Enum":      ("typed.mods.factories.generics", "Enum"),
    "Single":    ("typed.mods.factories.generics", "Single"),
    "Null":      ("typed.mods.factories.generics", "Null"),
    "Len":       ("typed.mods.factories.generics", "Len"),
    "Maybe":     ("typed.mods.factories.generics", "Maybe"),

    "model":     ("typed.mods.models", "model"),
    "value":     ("typed.mods.models", "value"),
    "validate":  ("typed.mods.models", "validate"),

    "Nill":      ("typed.mods.types.base", "Nill"),
    "Any":       ("typed.mods.types.base", "Any"),
    "Int":       ("typed.mods.types.base", "Int"),
    "Str":       ("typed.mods.types.base", "Str"),
    "Float":     ("typed.mods.types.base", "Float"),
    "Bool":      ("typed.mods.types.base", "Bool"),
    "Bytes":     ("typed.mods.types.base", "Bytes"),
    "Self":      ("typed.mods.types.base", "Self"),
    "Cls":       ("typed.mods.types.base", "Cls"),
    "Tuple":     ("typed.mods.types.base", "Tuple"),
    "List":      ("typed.mods.types.base", "List"),
    "Set":       ("typed.mods.types.base", "Set"),
    "Dict":      ("typed.mods.types.base", "Dict"),
    "Pattern":   ("typed.mods.types.base", "Pattern"),
    "TYPE":      ("typed.mods.types.base", "TYPE"),

    "Function":  ("typed.mods.types.func", "Function"),
    "Hinted":    ("typed.mods.types.func", "Hinted"),
    "Typed":     ("typed.mods.types.func", "Typed"),
    "Lazy":      ("typed.mods.types.func", "Lazy"),

    "name":      ("typed.mods.general", "name"),
    "names":     ("typed.mods.general", "names"),
    "null":      ("typed.mods.general", "null"),
    "convert":   ("typed.mods.general", "convert"),
    "new":       ("typed.mods.general", "new"),
    "var":       ("typed.mods.general", "var"),
    "_":         ("typed.mods.general", "_"),
    "append":    ("typed.mods.general", "append"),
    "switch":    ("typed.mods.general", "switch"),
    "func":      ("typed.mods.general", "func"),
}


def __getattr__(name):
    try:
        module_name, attr_name = __lazy__[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None

    module = __import__(module_name)
    attr = getattr(module, attr_name)
    globals()[name] = attr
    return attr


def __dir__():
    return sorted(set(globals().keys()) | set(__all__))

if __lsp__:
    from typed.mods.decorators import typed

    from typed.mods.factories.base import Union, Prod
    from typed.mods.factories.generics import (
        Inter, Filter, Compl, Regex, Interval, Range, Not, Enum,
        Single, Null, Len, Maybe
    )
    from typed.mods.models import model, value, validate
    from typed.mods.types.base import (
        Nill, Any, Int, Str, Float, Bool, Bytes, Self, Cls,
        Tuple, List, Set, Dict, Pattern, TYPE
    )
    from typed.mods.types.func import Function, Hinted, Typed, Lazy
    from typed.mods.general import name, names, null, new, convert, _, var, switch, func
