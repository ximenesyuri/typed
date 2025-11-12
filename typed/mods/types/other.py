from typed.mods.meta.other import PATTERN, TIMEZONE
from typed.mods.types.base import Str

Pattern = PATTERN("Pattern", (Str,), {"__display__": "Pattern", "__null__": ""})
TimeZone = TIMEZONE("TimeZone", (Str,), {"__display__": "TimeZone", "__null__": ""})
