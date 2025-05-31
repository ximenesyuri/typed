from typed.main import typed
from typed.mods.factories.base     import Prod
from typed.mods.factories.generics import Filter, Regex, Range
from typed.mods.types.base         import Json, Str, Any, Dict
from typed.mods.helper_examples    import _is_json_table, _is_json_flat

# Json
JsonTable     = Filter(Json, typed(_is_json_table))
JsonFlat      = Filter(Dict(Str, Any), typed(_is_json_flat))
JsonFlatEntry = Regex(r'^[a-zA-Z0-9_.]+$')

Env = Regex(r"^[A-Z0-9_]+$")

# Color
RGB = Prod(Range(0, 255), 3)
HEX = Regex(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
HSL = Prod(Range(0, 360), Range(0, 100), Range(0, 100))

# General
Email = Regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
HttpUrl = Regex(r'^https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:[/?].*)?$')

# Network
IPv4 = Regex(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$') 
