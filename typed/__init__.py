from typed.mods.loader import lazy

__imports__ = {
    "typed.core":      None,
    "typed.meta":      None,
    "typed.types":     None,
    "typed.factory":   None,
    "typed.decorator": None,
}

if lazy(__imports__):
    from typed.core      import *
    from typed.meta      import *
    from typed.types     import *
    from typed.factory   import *
    from typed.decorator import *
