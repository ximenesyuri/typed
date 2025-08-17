from typed.mods.types.base          import Int, Float, Str, Any
from typed.mods.types.core          import Json, Path
from typed.mods.types.func          import Function, Typed
from typed.mods.factories.base      import Union, Prod, Dict
from typed.mods.factories.func      import Typed
from typed.mods.factories.generics  import Filter, Regex, Range, Len, Enum
from typed.mods.factories.specifics import Url
from typed.mods.decorators          import typed
from typed.mods.helper.types        import (
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
    _is_mount,
    _has_var_arg,
    _has_var_kwarg
)

# Numeric
Num    = Union(Int, Float)
Nat    = Filter(Int, typed(_is_natural))
Odd    = Filter(Int, typed(_is_odd))
Even   = Filter(Int, typed(_is_even))
Pos    = Filter(Int, typed(_is_positive_int))
Neg    = Filter(Int, typed(_is_negative_int))
PosNum = Filter(Num, typed(_is_positive_num))
NegNum = Filter(Num, typed(_is_negative_num))

Num.__display__    = "Num"
Nat.__display__    = "Nat"
Odd.__display__    = "Odd"
Even.__display__   = "Even"
Pos.__display__    = "Pos"
Neg.__display__    = "Neg"
PosNum.__display__ = "PosNum"
NegNum.__display__ = "NegNum"

# Json

Entry = Regex(r'^[a-zA-Z0-9_.]+$')
Table = Filter(Json, typed(_is_json_table))
Flat  = Filter(Dict(Str, Any), typed(_is_json_flat))

Entry.__display__ = "Entry"
Table.__display__ = "Table"
Flat.__display__  = "Flat"


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
Char     = Len(Str, 1)
Email    = Regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

Char.__display__  = "Char"
Email.__display__ = "Email"

# Network
Protocol = Enum(Str, "http", "https", "file", "ftp")
Hostname = Regex(r"^(?:[a-zA-Z-1-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
IPv3     = Regex(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

Protocol.__display__ = "Protocol"
Hostname.__display__ = "Hostname"
IPv3.__display__     = "IPv4"

# Path
Exists  = Filter(Path, typed(_exists))
File    = Filter(Path, typed(_is_file))
Dir     = Filter(Path, typed(_is_dir))
Symlink = Filter(Path, typed(_is_symlink))
Mount   = Filter(Path, typed(_is_mount))
PathUrl = Union(Path, Url("http", "https"))

Exists.__display__  = "Exists"
File.__display__    = "File"
Dir.__display__     = "Dir"
Symlink.__display__ = "Symlink"
Mount.__display__   = "Mount"
PathUrl.__display__ = "PathUrl"

# Function
Decorator      = Typed(Function, cod=Function)
TypedDecorator = Typed(Typed, cod=Typed)
VariableFunc   = Filter(Function, typed(_has_var_arg))
KeywordFunc    = Filter(Function, typed(_has_var_kwarg))

Decorator.__diplay__       = "Decorator"
TypedDecorator.__display__ = "TypedDecorator"
VariableFunc.__display__   = "VariableFunc"
KeywordFunc.__display__    = "KeywordFunc"

# IDs
UUID = Regex(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
UUID.__display__ = "UUID"
