import os
from typed.mods.types.base import Int, Str, Float, Any, Json, Bool, Path
from typed.mods.factories.base import Union

def _is_natural(x: Int) -> Bool:
    """
    Checks if an integer is a natural number.
    (Assuming Bourbaki convention)
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

    from typed.examples import JsonEntry
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

def _install(lib, venv=None):
    from importlib.util import find_spec
    from pathlib import Path as _Path
    import os
    import subprocess
    if find_spec(lib) is not None:
        return

    if venv is None:
        current = _Path.cwd()
        found = False
        for parent in [current] + list(current.parents):
            possible = parent / '.venv'
            if possible.exists() and (possible / 'bin' / 'python').exists():
                venv = str(possible)
                found = True
                break
        if not found:
            return 'Error: No virtual environment found (.venv not located in parent directories)'

    if os.name == 'nt':
        pip_executable = os.path.join(venv, 'Scripts', 'pip.exe')
    else:
        pip_executable = os.path.join(venv, 'bin', 'pip')

    if not os.path.isfile(pip_executable):
        return f"Error: pip not found in the virtual environment at '{venv}'."

    try:
        subprocess.check_call([pip_executable, 'install', lib, '-q'])
        return f"'{lib}' has been installed in venv: {venv}"
    except subprocess.CalledProcessError as e:
        return f"Error installing '{lib}' in venv: {venv}. Detail: {str(e)}"

def _is_markdown(content: Str) -> Bool:
    _install('markdown')
    from markdown import markdown
    try:
        html = markdown(content)
        return True
    except Exception as e:
        return False
