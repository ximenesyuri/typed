import os
from typed.mods.factories.base import Union
from typed.mods.factories.generics import Regex, Null, Filter
from typed.mods.factories.extra import Url
from typed.mods.types.base import Any, Str, Bool
from typed.mods.types.func import Condition

Path = Union(Regex(r"^/?(?:(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?|/?)$"), Null(Str))

def _exists(path: Path) -> Bool:
    return os.path.exists(path)

def _is_file(path: Path) -> Bool:
    return os.path.isfile(path)

def _is_dir(path: Path) -> Bool:
    return os.path.isdir(path)

def _is_symlink(path: Path) -> Bool:
    return os.path.islink(path)

def _is_mount(path: Path) -> Bool:
    return os.path.ismount(path)

Exists  = Filter(Path, Condition(_exists))
File    = Filter(Path, Condition(_is_file))
Dir     = Filter(Path, Condition(_is_dir))
Symlink = Filter(Path, Condition(_is_symlink))
Mount   = Filter(Path, Condition(_is_mount))
PathUrl = Union(Path, Url("http", "https"))

Path.__display__    = "Path"
Exists.__display__  = "Exists"
File.__display__    = "File"
Dir.__display__     = "Dir"
Symlink.__display__ = "Symlink"
Mount.__display__   = "Mount"
PathUrl.__display__ = "PathUrl"

Path.__null__    = ""
Exists.__null__  = ""
File.__null__    = ""
Dir.__null__     = ""
Symlink.__null__ = ""
Mount.__null__   = ""
PathUrl.__null__ = ""
