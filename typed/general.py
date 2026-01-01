from importlib import import_module as __import__
from typing import TYPE_CHECKING as __lsp__

__all__ = [
    "name", "names", "null", "new", "poly", "convert"
]

__lazy__ = {
    "name":    ("typed.mods.general", "name"),
    "names":   ("typed.mods.general", "names"),
    "null":    ("typed.mods.general", "null"),
    "new":     ("typed.mods.general", "new"),
    "poly":    ("typed.mods.general", "poly"),
    "convert": ("typed.mods.general", "convert"),
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
    from typed.mods.general import name, names, null, new, poly, convert
