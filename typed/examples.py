from typed.mods.factories.generics import Filter
from typed.mods.types.base import Json, Str, Any, Dict, Regex
from typed.mods.helper_examples import _is_json_table, _is_json_flat

JsonTable     = Filter(Json, _is_json_table)
JsonFlat      = Filter(Dict(Str, Any), _is_json_flat)
JsonFlatEntry = Regex(r'^[a-zA-Z0-9_.]+$')
