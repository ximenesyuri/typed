from importlib import import_module as __import__
from typing import TYPE_CHECKING as __lsp__

__all__ = [
    "LAZY_MODEL", "EAGER_MODEL",
    "MODEL", "EXACT", "ORDERED", "RIGID",
    "Model", "Optional", "Exact", "Ordered", "Rigid",
    "model", "optional", "mandatory", "exact", "ordered", "rigid",
    "drop", "validate", "eval", "value", "hasvalue", "Default", "expression"
]

__lazy__ = {
    "LAZY_MODEL":   ("typed.mods.models", "LAZY_MODEL"),
    "EAGER_MODEL":  ("typed.mods.models", "EAGER_MODEL"),
    "MODEL":        ("typed.mods.models", "MODEL"),
    "EXACT":        ("typed.mods.models", "EXACT"),
    "ORDERED":      ("typed.mods.models", "ORDERED"),
    "RIGID":        ("typed.mods.models", "RIGID"),
    "Model":        ("typed.mods.models", "Model"),
    "Optional":     ("typed.mods.models", "Optional"),
    "Exact":        ("typed.mods.models", "Exact"),
    "Ordered":      ("typed.mods.models", "Ordered"),
    "Rigid":        ("typed.mods.models", "Rigid"),
    "model":        ("typed.mods.models", "model"),
    "optional":     ("typed.mods.models", "optional"),
    "mandatory":    ("typed.mods.models", "mandatory"),
    "exact":        ("typed.mods.models", "exact"),
    "ordered":      ("typed.mods.models", "ordered"),
    "rigid":        ("typed.mods.models", "rigid"),
    "drop":         ("typed.mods.models", "drop"),
    "validate":     ("typed.mods.models", "validate"),
    "eval":         ("typed.mods.models", "eval"),
    "value":        ("typed.mods.models", "value"),
    "hasvalue":     ("typed.mods.models", "hasvalue"),
    "Default":      ("typed.mods.models", "Default"),
    "expression":   ("typed.mods.models", "expression")
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
    from typed.mods.models import (
        LAZY_MODEL, EAGER_MODEL,
        MODEL, EXACT, ORDERED, RIGID,
        Model, Optional, Exact, Ordered, Rigid,
        model, optional, mandatory, exact, ordered, rigid,
        drop, validate, eval, value, hasvalue, Default, expression
    )

