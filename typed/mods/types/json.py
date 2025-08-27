from typed.mods.types.base import Bool, Any, Str
from typed.mods.factories.base import Union
from typed.mods.types.factories import Dict, Set, List
from typed.mods.factories.generics import Regex, Filter
from typed.mods.decorators import typed

Json = Union(Dict(Any), Set(Any), List(Any))
Entry = Regex(r'^[a-zA-Z0-9_.]+$')

def _is_json_table(data: Any) -> Bool:
    """
    Checks if the data is a valid JSON Table structure
    (list of dicts with same keys).
    """
    if not isinstance(data, list):
        return False
    if not all(isinstance(item, dict) for item in data):
        return False
    if data:
        first_keys = set(data[0].keys())
        if not all(set(item.keys()) == first_keys for item in data):
            return False
    return True

def _is_json_flat(data: Json) -> Bool:
    """
    Checks if the data represents a 'flat' JSON structure,
    where values are primitive types or None.
    """
    if not isinstance(data, dict):
        return False
    for key in data.keys():
        if not isinstance(key, Entry):
            return False
    return True

Table = Filter(Json, typed(_is_json_table))
Flat  = Filter(Dict(Str, Any), typed(_is_json_flat))

Json.__display__  = "Json"
Entry.__display__ = "Entry"
Table.__display__ = "Table"
Flat.__display__  = "Flat"

Json.__null__  = {}
Entry.__null__ = None
Table.__null__ = {}
Flat.__null__  = {}
