from importlib import import_module as __import__
from typing import TYPE_CHECKING as __lsp__

__all__ = [
    "__UNIVERSE__", "_TYPE_", "_ABSTRACT_", "_UNIVERSAL_", "_META_", "_DISCOURSE_", "_PARAMETRIC_",
    "ABSTRACT", "UNIVERSAL", "META", "DISCOURSE", "PARAMETRIC",
    "NILL", "ANY", "INT", "BOOL", "STR", "FLOAT", "BYTES", "TUPLE", "LIST", "DICT", "SET", "PATTERN",
    "CALLABLE", "BUILTIN", "FUNCTION", "LAMBDA", "PARTIAL",
    "CLASS", "BOUND_METHOD", "UNBOUND_METHOD", "METHOD",
    "ATTR_FUNC", "DOM_FUNC", "COD_FUNC", "COMP_FUNC",
    "DOM_HINTED", "COD_HINTED", "HINTED", "DOM_TYPED", "COD_TYPED", "TYPED",
    "FACTORY", "OPERATION", "DEPENDENT", "CONDITION", "LAZY"
]

__lazy__ = {
    "__UNIVERSE__":     ("typed.mods.meta.base", "__UNIVERSE__"),
    "_TYPE_":           ("typed.mods.meta.base", "_TYPE_"),
    "_ABSTRACT_":       ("typed.mods.meta.base", "_ABSTRACT_"),
    "_UNIVERSAL_":      ("typed.mods.meta.base", "_UNIVERSAL_"),
    "_META_":           ("typed.mods.meta.base", "_META_"),
    "_DISCOURSE_":      ("typed.mods.meta.base", "_DISCOURSE_"),
    "_PARAMETRIC_":     ("typed.mods.meta.base", "_PARAMETRIC_"),
    "ABSTRACT":         ("typed.mods.types.base", "ABSTRACT"),
    "UNIVERSAL":        ("typed.mods.types.base", "UNIVERSAL"),
    "META":             ("typed.mods.types.base", "META"),
    "DISCOURSE":        ("typed.mods.types.base", "DISCOURSE"),
    "PARAMETRIC":       ("typed.mods.types.base", "PARAMETRIC"),
    "NILL":             ("typed.mods.meta.base", "NILL"),
    "ANY":              ("typed.mods.meta.base", "ANY"),
    "INT":              ("typed.mods.meta.base", "INT"),
    "BOOL":             ("typed.mods.meta.base", "BOOL"),
    "STR":              ("typed.mods.meta.base", "STR"),
    "FLOAT":            ("typed.mods.meta.base", "FLOAT"),
    "BYTES":            ("typed.mods.meta.base", "BYTES"),
    "TUPLE":            ("typed.mods.meta.base", "TUPLE"),
    "LIST":             ("typed.mods.meta.base", "LIST"),
    "DICT":             ("typed.mods.meta.base", "DICT"),
    "SET":              ("typed.mods.meta.base", "SET"),
    "PATTERN":          ("typed.mods.meta.other", "PATTERN"),
    "CALLABLE":         ("typed.mods.meta.func", "CALLABLE"),
    "BUILTIN":          ("typed.mods.meta.func", "BUILTIN"),
    "FUNCTION":         ("typed.mods.meta.func", "FUNCTION"),
    "PARTIAL":          ("typed.mods.meta.func", "PARTIAL"),
    "ATTR_FUNC":        ("typed.mods.meta.func", "ATTR_FUNC"),
    "DOM_FUNC":         ("typed.mods.meta.func", "DOM_FUNC"),
    "COD_FUNC":         ("typed.mods.meta.func", "COD_FUNC"),
    "COMP_FUNC":        ("typed.mods.meta.func", "COMP_FUNC"),
    "LAMBDA":           ("typed.mods.meta.func", "LAMBDA"),
    "CLASS":            ("typed.mods.meta.func", "CLASS"),
    "BOUND_METHOD":     ("typed.mods.meta.func", "BOUND_METHOD"),
    "UNBOUND_METHOD":   ("typed.mods.meta.func", "UNBOUND_METHOD"),
    "METHOD":           ("typed.mods.meta.func", "METHOD"),
    "DOM_HINTED":       ("typed.mods.meta.func", "DOM_HINTED"),
    "COD_HINTED":       ("typed.mods.meta.func", "COD_HINTED"),
    "HINTED":           ("typed.mods.meta.func", "HINTED"),
    "DOM_TYPED":        ("typed.mods.meta.func", "DOM_TYPED"),
    "COD_TYPED":        ("typed.mods.meta.func", "COD_TYPED"),
    "TYPED":            ("typed.mods.meta.func", "TYPED"),
    "FACTORY":          ("typed.mods.meta.func", "FACTORY"),
    "OPERATION":        ("typed.mods.meta.func", "OPERATION"),
    "DEPENDENT":        ("typed.mods.meta.func", "DEPENDENT"),
    "CONDITION":        ("typed.mods.meta.func", "CONDITION"),
    "LAZY":             ("typed.mods.meta.func", "LAZY"),

    "_MODEL_":          ("typed.mods.meta.models", "_MODEL_"),
    "_LAZY_MODEL_":     ("typed.mods.meta.func", "_LAZY_MODEL_"),
    "MODEL_META":       ("typed.mods.meta.func", "MODEL_META"),
    "MODEL_INSTANCE":   ("typed.mods.meta.func", "MODEL_INSTANCE"),
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
    from typed.mods.meta.base import (
        __UNIVERSE__, _TYPE_, _ABSTRACT_, _UNIVERSAL_, _META_, _DISCOURSE_, _PARAMETRIC_,
        NILL, ANY, INT, BOOL, STR, FLOAT, BYTES, TUPLE, LIST, DICT, SET, PATTERN
    )
    from typed.mods.meta.func import (
        CALLABLE, BUILTIN, FUNCTION, LAMBDA, PARTIAL,
        CLASS, BOUND_METHOD, UNBOUND_METHOD, METHOD,
        ATTR_FUNC, DOM_FUNC, COD_FUNC, COMP_FUNC,
        DOM_HINTED, COD_HINTED, HINTED,
        DOM_TYPED, COD_TYPED, TYPED,
        FACTORY, OPERATION, DEPENDENT, CONDITION,
        LAZY
    )
    from typed.mods.meta.models import (
        _LAZY_MODEL_, _MODEL_,
        MODEL_META, MODEL_INSTANCE
    )
