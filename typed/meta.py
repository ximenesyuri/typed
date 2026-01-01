from importlib import import_module as __import__
from typing import TYPE_CHECKING as __lsp__

__all__ = [
    "__UNIVERSE__", "_TYPE_", "_ABSTRACT_", "_UNIVERSAL_", "_META_", "_DISCOURSE_", "_PARAMETRIC_",
    "NILL", "ANY", "INT", "BOOL", "STR", "FLOAT", "BYTES", "TUPLE", "LIST", "DICT", "SET", "PATTERN",

    "CALLABLE", "BUILTIN", "FUNCTION", "LAMBDA", "CLASS", "BOUND_METHOD", "UNBOUND_METHOD", "METHOD",
    "HINTED_DOM", "HINTED_COD", "HINTED", "TYPED_DOM", "TYPED_COD", "TYPED", "FACTORY", "OPERATION", "DEPENDENT", "CONDITION",
]

__lazy__ = {
    "__UNIVERSE__":     ("typed.mods.meta.base", "__UNIVERSE__"),
    "_TYPE_":           ("typed.mods.meta.base", "_TYPE_"),
    "_ABSTRACT_":       ("typed.mods.meta.base", "_ABSTRACT_"),
    "_UNIVERSAL_":      ("typed.mods.meta.base", "_UNIVERSAL_"),
    "_META_":           ("typed.mods.meta.base", "_META_"),
    "_DISCOURSE_":      ("typed.mods.meta.base", "_DISCOURSE_"),
    "_PARAMETRIC_":     ("typed.mods.meta.base", "_PARAMETRIC_"),
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
    "LAMBDA":           ("typed.mods.meta.func", "LAMBDA"),
    "CLASS":            ("typed.mods.meta.func", "CLASS"),
    "BOUND_METHOD":     ("typed.mods.meta.func", "BOUND_METHOD"),
    "UNBOUND_METHOD":   ("typed.mods.meta.func", "UNBOUND_METHOD"),
    "METHOD":           ("typed.mods.meta.func", "METHOD"),
    "HINTED_DOM":       ("typed.mods.meta.func", "HINTED_DOM"),
    "HINTED_COD":       ("typed.mods.meta.func", "HINTED_COD"),
    "HINTED":           ("typed.mods.meta.func", "HINTED"),
    "TYPED_DOM":        ("typed.mods.meta.func", "TYPED_DOM"),
    "TYPED_COD":        ("typed.mods.meta.func", "TYPED_COD"),
    "TYPED":            ("typed.mods.meta.func", "TYPED"),
    "FACTORY":          ("typed.mods.meta.func", "FACTORY"),
    "OPERATION":        ("typed.mods.meta.func", "OPERATION"),
    "DEPENDENT":        ("typed.mods.meta.func", "DEPENDENT"),
    "CONDITION":        ("typed.mods.meta.func", "CONDITION"),
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
        CALLABLE, BUILTIN, FUNCTION, LAMBDA,
        CLASS, BOUND_METHOD, UNBOUND_METHOD, METHOD,
        HINTED_DOM, HINTED_COD, HINTED,
        TYPED_DOM, TYPED_COD, TYPED,
        FACTORY, OPERATION, DEPENDENT, CONDITION
    )
