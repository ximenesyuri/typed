from typing import Type
from functools import lru_cache as cache

@cache
def Extension(ext: str) -> Type:
    from typed.mods.types.base import Path
    class _Extension(type(Path)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Path):
                return False
            parts = instance.split('.')
            return parts[-1] == ext
    return _Extension(f'Extension({ext})', (Path,), {})
