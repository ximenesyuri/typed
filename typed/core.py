from importlib import import_module as __import__
from typing import TYPE_CHECKING as __lsp__

__all__ = [
    "TYPESYSTEM",
    "type", "typemap", "new",
    "term", "sub", "sup",
    "display", "name", "null"
]

__lazy__ = {
    "TYPESYSTEM": ("typed.mods.core", "TYPESYSTEM"), 
    
    "type":    ("typed.mods.core", "type"),
    "typemap": ("typed.mods.core", "typemap"),
    "new":     ("typed.mods.core", "new"),
    
    "term":   ("typed.mods.core", "term"),
    "sub":    ("typed.mods.core", "sub"),
    "sup":     ("typed.mods.core", "sup"),
    "display": ("typed.mods.core", "display"),
    "name":    ("typed.mods.core", "name"),
    "null":    ("typed.mods.core", "null")
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
    from typed.mods.core import (
        TYPESYSTEM,
        type, typemap, new,
        term, sub, sup,
        display, name, null
)
