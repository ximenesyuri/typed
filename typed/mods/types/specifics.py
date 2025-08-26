from typed.mods.types.base          import Str
from typed.mods.factories.base      import Prod
from typed.mods.factories.func      import Typed
from typed.mods.factories.generics  import Regex, Range, Len, Enum

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
IPv4     = Regex(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

Protocol.__display__ = "Protocol"
Hostname.__display__ = "Hostname"
IPv4.__display__     = "IPv4"

# IDs
UUID = Regex(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
UUID.__display__ = "UUID"
