from importlib import import_module as __import__
from typing import TYPE_CHECKING as __lsp__

__all__ = [
    "Union", "Prod", "Unprod",
    "Inter", "Filter", "Compl", "Regex", "Interval", "Range",
    "Not", "Enum", "Single", "Null", "NotNull", "Len", "Maybe",
    "ATTR", "SUBTYPES", "NOT"
]

__lazy__ = {
    "Union":    ("typed.mods.factories.base",       "Union"),
    "Prod":     ("typed.mods.factories.base",       "Prod"),
    "Unprod":   ("typed.mods.factories.base",       "Unprod"),
    "Inter":    ("typed.mods.factories.generics",   "Inter"),
    "Filter":   ("typed.mods.factories.generics",   "Filter"),
    "Compl":    ("typed.mods.factories.generics",   "Compl"),
    "Regex":    ("typed.mods.factories.generics",   "Regex"),
    "Interval": ("typed.mods.factories.generics",   "Interval"),
    "Range":    ("typed.mods.factories.generics",   "Range"),
    "Not":      ("typed.mods.factories.generics",   "Not"),
    "Enum":     ("typed.mods.factories.generics",   "Enum"),
    "Single":   ("typed.mods.factories.generics",   "Single"),
    "Null":     ("typed.mods.factories.generics",   "Null"),
    "NotNull":  ("typed.mods.factories.generics",   "NotNull"),
    "Len":      ("typed.mods.factories.generics",   "Len"),
    "Maybe":    ("typed.mods.factories.generics",   "Maybe"),
    "ATTR":     ("typed.mods.factories.meta",       "ATTR"),
    "SUBTYPES": ("typed.mods.factories.meta",       "SUBTYPES"),
    "NOT":      ("typed.mods.factories.meta",       "NOT"),
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
    from typed.mods.factories.base import Union, Prod, Unprod
    from typed.mods.factories.generics import (
        Inter, Filter, Compl, Regex, Interval, Range,
        Not, Enum, Single, Null, NotNull, Len, Maybe
    )
    from typed.mods.factories.meta import ATTR, SUBTYPES, NOT
