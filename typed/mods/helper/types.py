import os
from typed.mods.types.func import Function
from typed.mods.types.base import Int, Str, Float, Any, Json, Bool, Path
from typed.mods.factories.base import Union

def _is_natural(x: Int) -> Bool:
    """
    Checks if an integer is a natural number.
        > Assuming Bourbaki convention, so that
        > _is_natural(0) is True
    """
    return x >= 0

def _is_odd(x: Int) -> Bool:
  """
  Checks if an integer number is odd.
  """
  return x % 2 != 0

def _is_even(x: Int) -> Bool:
  """
  Checks if an integer number is even.
  """
  return x % 2 == 0

def _is_positive_int(x: Int) -> Bool:
    """
    Checks if an integer is positive.
    """
    return x > 0

def _is_negative_int(x: Int) -> Bool:
    """
    Checks if an integer is negative.
    """
    return x < 0

def _is_positive_num(x: Union(Int, Float)) -> Bool:
    """
    Checks if an integer is positive.
    """
    return x > 0

def _is_negative_num(x: Union(Int, Float)) -> Bool:
    """
    Checks if an integer is negative.
    """
    return x < 0

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

    from typed.mods.types.other import JsonEntry
    for key in data.keys():
        if not isinstance(key, JsonEntry):
            return False
    return True

def _exists(path: Path) -> Bool:
    """
    Checks if a path exists.
    """
    return os.path.exists(path)

def _is_file(path: Path) -> Bool:
    """
    Checks if a path is an existing file.
    """
    return os.path.isfile(path)

def _is_dir(path: Path) -> Bool:
    """
    Checks if a path is an existing dir.
    """
    return os.path.isdir(path)

def _is_symlink(path: Path) -> Bool:
    """
    Checks if a path is a symbolic link.
    """
    return os.path.islink(path)

def _is_mount(path: Path) -> Bool:
    """
    Checks if a path is a a mount point.
    """
    return os.path.ismount(path)

def _has_var_arg(func: Function) -> Bool:
    signature = inspect.signature(func)
    for param in signature.parameters.values():
        if param.kind == param.VAR_POSITIONAL:
            return True
    return False

def _has_var_kwarg(func: Function) -> Bool:
    signature = inspect.signature(func)
    for param in signature.parameters.values():
        if param.kind == param.VAR_KEYWORD:
            return True
    return False
