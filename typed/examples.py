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
