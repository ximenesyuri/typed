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

class TIMEZONE(STR):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import Str
        from zoneinfo import ZoneInfo
        if not isinstance(instance, Str):
            return False
        try:
            ZoneInfo(instance)
            return True
        except:
            return False
