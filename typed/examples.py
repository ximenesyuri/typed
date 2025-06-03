from typed.main import typed
from typed.mods.factories.base     import Prod, Union, Null
from typed.mods.factories.generics import Filter, Regex, Range
from typed.mods.types.base         import Json, Str, Any, Dict
from typed.mods.helper_examples    import _is_json_table, _is_json_flat

# Json
JsonTable     = Filter(Json, typed(_is_json_table))
JsonFlat      = Filter(Dict(Str, Any), typed(_is_json_flat))
JsonEntry = Regex(r'^[a-zA-Z0-9_.]+$')

JsonTable.__display__ = "JsonTable"
JsonFlat.__display__  = "JsonFlat"
JsonEntry.__display__ = "JsonEntry"

# System 
Env = Regex(r"^[A-Z0-9_]+$")

Env.__display__ = "Env"

# Color
RGB = Prod(Range(0, 255), 3)
HEX = Regex(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
HSL = Prod(Range(0, 360), Range(0, 100), Range(0, 100))

RGB.__display__ = "RGB"
HEX.__display__ = "HEX"
HSL.__display__ = "HSL"

# Text
Email      = Regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
HttpUrl    = Regex(r'^https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:[/?].*)?$')
RclonePath = Union(Regex(r'^([^/:\r\n*?\"<>|\\]+:/??|(?:[^/:\r\n*?\"<>|\\]+:)?(?:/?(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?))$'), Null(Str))

Email.__display__      = "Email"
HttpUrl.__display__    = "HttpUrl"
RclonePath.__display__ = "RclonePath"

# Network
IPv4 = Regex(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
IPv4.__display__ = "IPv4"
