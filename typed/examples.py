from typed.main import typed
from typed.mods.factories.generics import Filter, Regex
from typed.mods.types.base import Json, Str, Any, Dict
from typed.mods.helper_examples import _is_json_table, _is_json_flat

JsonTable     = Filter(Json, typed(_is_json_table))
JsonFlat      = Filter(Dict(Str, Any), typed(_is_json_flat))
JsonFlatEntry = Regex(r'^[a-zA-Z0-9_.]+$')
