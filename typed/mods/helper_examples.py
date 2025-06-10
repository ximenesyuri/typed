def _is_json_table(data):
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

def _is_json_flat(data):
    """
    Checks if the data represents a 'flat' JSON structure,
    where values are primitive types or None.
    """
    if not isinstance(data, dict):
        return False

    primitive_types = (str, int, float, bool, type(None))
    for value in data.values():
        if not isinstance(value, primitive_types):
            return False
    return True
