def lazy(target):
    import sys
    from importlib import import_module
    from typing import TYPE_CHECKING

    if isinstance(target, str):
        class LazyLoad:
            __slots__ = ('_lib_name', '_module')

            def __init__(self, lib_name: str):
                self._lib_name = lib_name
                self._module = None

            def __getattr__(self, attr: str):
                if self._module is None:
                    self._module = import_module(self._lib_name)
                return getattr(self._module, attr)

        return LazyLoad(target)

    elif isinstance(target, dict):
        from sys import _getframe
        caller_frame = _getframe(1)
        caller_globals = caller_frame.f_globals
        caller_name = caller_globals.get("__name__", "<unknown>")

        all_names = []
        lazy_map = {}
        wildcard_modules = []

        for module_path, attr_names in target.items():
            if attr_names is None:
                wildcard_modules.append(module_path)
            else:
                for attr_name in attr_names:
                    all_names.append(attr_name)
                    lazy_map[attr_name] = (module_path, attr_name)

        caller_globals["__all__"] = all_names
        caller_globals["__lazy__"] = lazy_map
        caller_globals["__wildcards__"] = wildcard_modules

        def __getattr__(name_str):
            import sys
            current_module = sys.modules.get(caller_name)
            if current_module is None:
                raise ImportError(f"Cannot find module {caller_name!r}")

            current_globals = current_module.__dict__
            lazy_map = current_globals.get("__lazy__", {})
            wildcards = current_globals.get("__wildcards__", [])
            if name_str in lazy_map:
                module_name, attr_name = lazy_map[name_str]
                module = import_module(module_name)
                obj = getattr(module, attr_name)
                current_globals[name_str] = obj
                return obj

            for mod_name in wildcards:
                try:
                    module = import_module(mod_name)
                    if hasattr(module, name_str) and not name_str.startswith("_"):
                        obj = getattr(module, name_str)
                        current_globals[name_str] = obj
                        return obj
                except ImportError:
                    continue

            raise AttributeError(
                f"module {caller_name!r} has no attribute {name_str!r}"
            )

        def __dir__():
            current_module = sys.modules.get(caller_name)
            if current_module:
                return sorted(set(current_module.__dict__.keys()) | set(current_module.__dict__.get("__all__", [])))
            return []

        caller_globals["__getattr__"] = __getattr__
        caller_globals["__dir__"] = __dir__

        return TYPE_CHECKING

    else:
        raise TypeError("lazy() expects a dict (module-level setup) or str (library proxy).")


def __typed__(enabled=True, **configs):
    from sys import _getframe
    from typed.mods.config import config

    config.enabled = enabled
    for key, value in configs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown typed configuration: {key}")

    caller_frame = _getframe(1)
    caller_globals = caller_frame.f_globals

    original_getattr = caller_globals.get("__getattr__")

    def __getattr__(name):
        import typed

        if name in typed.__all__:
            obj = getattr(typed, name)
            caller_globals[name] = obj
            return obj

        if original_getattr is not None:
            return original_getattr(name)

        raise AttributeError(f"module '{caller_globals.get('__name__', 'unknown')}' has no attribute '{name}'")

    caller_globals["__getattr__"] = __getattr__
