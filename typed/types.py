from importlib import import_module as __import__
from typing import TYPE_CHECKING as __lsp__

__all__ = [
    "TYPE", "ABSTRACT", "UNIVERSAL",
    "META", "DISCOURSE", "PARAMETRIC",
    "Nill", "Any",
    "Int", "Str", "Float", "Bool", "Bytes", "Self", "Cls",
    "Tuple", "List", "Set", "Dict",
    "Pattern",
    "Callable", "Builtin", "Lambda", "Function", "Composable",
    "Class", "BoundMethod", "UnboundMethod", "Method",
    "HintedDom", "HintedCod", "Hinted",
    "TypedDom", "TypedCod", "Typed",
    "Factory", "Condition", "Operation", "Dependent"
]

__lazy__ = {
    "TYPE":       ("typed.mods.types.base", "TYPE"),
    "ABSTRACT":   ("typed.mods.types.base", "ABSTRACT"),
    "UNIVERSAL":  ("typed.mods.types.base", "UNIVERSAL"),
    "META":       ("typed.mods.types.base", "META"),
    "DISCOURSE":  ("typed.mods.types.base", "DISCOURSE"),
    "PARAMETRIC": ("typed.mods.types.base", "PARAMETRIC"),
    "Nill":       ("typed.mods.types.base", "Nill"),
    "Any":        ("typed.mods.types.base", "Any"),
    "Int":        ("typed.mods.types.base", "Int"),
    "Str":        ("typed.mods.types.base", "Str"),
    "Float":      ("typed.mods.types.base", "Float"),
    "Bool":       ("typed.mods.types.base", "Bool"),
    "Bytes":      ("typed.mods.types.base", "Bytes"),
    "Self":       ("typed.mods.types.base", "Self"),
    "Cls":        ("typed.mods.types.base", "Cls"),
    "Tuple":      ("typed.mods.types.base", "Tuple"),
    "List":       ("typed.mods.types.base", "List"),
    "Set":        ("typed.mods.types.base", "Set"),
    "Dict":       ("typed.mods.types.base", "Dict"),
    "Pattern":    ("typed.mods.types.base", "Pattern"),
    "Callable":     ("typed.mods.types.func", "Callable"),
    "Builtin":      ("typed.mods.types.func", "Builtin"),
    "Lambda":       ("typed.mods.types.func", "Lambda"),
    "Function":     ("typed.mods.types.func", "Function"),
    "Composable":   ("typed.mods.types.func", "Composable"),
    "Class":        ("typed.mods.types.func", "Class"),
    "BoundMethod":  ("typed.mods.types.func", "BoundMethod"),
    "UnboundMethod":("typed.mods.types.func", "UnboundMethod"),
    "Method":       ("typed.mods.types.func", "Method"),
    "HintedDom":    ("typed.mods.types.func", "HintedDom"),
    "HintedCod":    ("typed.mods.types.func", "HintedCod"),
    "Hinted":       ("typed.mods.types.func", "Hinted"),
    "TypedDom":     ("typed.mods.types.func", "TypedDom"),
    "TypedCod":     ("typed.mods.types.func", "TypedCod"),
    "Typed":        ("typed.mods.types.func", "Typed"),
    "Factory":      ("typed.mods.types.func", "Factory"),
    "Condition":    ("typed.mods.types.func", "Condition"),
    "Operation":    ("typed.mods.types.func", "Operation"),
    "Dependent":    ("typed.mods.types.func", "Dependent")
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
    from typed.mods.types.base import (
        TYPE, ABSTRACT, UNIVERSAL, META, DISCOURSE, PARAMETRIC,
        Nill, Any, Int, Str, Float, Bool, Bytes,
        Self, Cls,
        Tuple, List, Set, Dict, Pattern
    )
    from typed.mods.types.func import (
        Callable, Builtin, Lambda, Function, Composable,
        Class, BoundMethod, UnboundMethod, Method,
        HintedDom, HintedCod, Hinted,
        TypedDom, TypedCod, Typed,
        Factory, Condition, Operation, Dependent
    )

