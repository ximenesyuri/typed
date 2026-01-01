from importlib import import_module as __import__
from typing import TYPE_CHECKING as __lsp__

__all__ = [
    "hinted",
    "typed",
    "factory",
    "condition",
    "operation",
    "dependent"
]

__lazy__ = {
    "hinted":    ("typed.mods.decorators", "hinted"),
    "typed":     ("typed.mods.decorators", "typed"),
    "factory":   ("typed.mods.decorators", "factory"),
    "condition": ("typed.mods.decorators", "condition"),
    "operation": ("typed.mods.decorators", "operation"),
    "dependent": ("typed.mods.decorators", "dependent"),
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
    from typed.mods.decorators import hinted, typed, factory, condition, operation, dependent
