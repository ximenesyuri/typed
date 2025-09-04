import re
from typed.mods.meta.base import STR

class PATTERN(STR):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import Str
        if not isinstance(instance, Str):
            return False
        try:
            re.compile(instance)
            return True
        except re.error:
            return False

    def __subclasscheck__(cls, subclass):
        return issubclass(subclass, cls)
