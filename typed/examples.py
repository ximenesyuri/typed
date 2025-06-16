from typed.main import typed
from typed.mods.factories.base     import Prod, Union, Null
from typed.mods.factories.generics import Filter, Regex, Range, Len
from typed.mods.types.base         import Int, Float, Json, Str, Any, Dict, Path
from typed.mods.helper.examples    import (
    _is_json_table,
    _is_json_flat,
    _is_natural,
    _is_positive_int,
    _is_negative_int,
    _is_positive_num,
    _is_negative_num,
    _is_odd,
    _is_even,
    _exists,
    _is_file,
    _is_dir,
    _is_symlink,
    _is_mount
)

# Numeric
Num    = Union(Int, Float)
Nat    = Filter(Int, typed(_is_natural))
Odd    = Filter(Int, typed(_is_odd))
Even   = Filter(Int, typed(_is_even))
PosInt = Filter(Int, typed(_is_positive_int))
NegInt = Filter(Int, typed(_is_negative_int))
PosNum = Filter(Num, typed(_is_positive_num))
NegNum = Filter(Num, typed(_is_negative_num))

Num.__display__    = "Num"
Nat.__display__    = "Nat"
Odd.__display__    = "Odd"
Even.__display__   = "Even"
PosInt.__display__ = "PosInt"
NegInt.__display__ = "NegInt"
PosNum.__display__ = "PosNum"
NegNum.__display__ = "NegNum"

# Json
JsonTable = Filter(Json, typed(_is_json_table))
JsonFlat  = Filter(Dict(Str, Any), typed(_is_json_flat))
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
Char  = Len(Str, 1)
Email = Regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

Char.__display    = "Char"
Email.__display__ = "Email"

# Path
Exists     = Filter(Path, typed(_exists))
File       = Filter(Path, typed(_is_file))
Dir        = Filter(Path, typed(_is_dir))
Symlink    = Filter(Path, typed(_is_symlink))
Mount      = Filter(Path, typed(_is_mount))
RclonePath = Union(Regex(r'^([^/:\r\n*?\"<>|\\]+:/??|(?:[^/:\r\n*?\"<>|\\]+:)?(?:/?(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?))$'), Null(Str))

Exists.__display__     = "Exists"
File.__display__       = "File"
Dir.__display__        = "Dir"
Symlink.__display__    = "Symlink"
Mount.__display__      = "Mount"
RclonePath.__display__ = "RclonePath"

# Network
Hostname = Regex(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
IPv4     = Regex(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
HttpUrl  = Regex(r'^https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:[/?].*)?$')

Hostname.__display__ = "Hostname"
IPv4.__display__     = "IPv4"
HttpUrl.__display__  = "HttpUrl"
