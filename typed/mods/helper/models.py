class _Optional:
    def __init__(self, typ, default_value):
        self.type = typ
        self.default_value = default_value

class _MODEL(type):
    def __instancecheck__(self, instance):
        t = type(instance)
        cls = instance.__class__ if not isinstance(instance, type) else instance
        return type(cls).__name__ == "_Model"

class _EXACT(type):
    def __instancecheck__(self, instance):
        t = type(instance)
        cls = instance.__class__ if not isinstance(instance, type) else instance
        return type(cls).__name__ == "_Exact"

class _CONDITIONAL(type):
    def __instancecheck__(self, instance):
        t = type(instance)
        cls = instance.__class__ if not isinstance(instance, type) else instance
        return type(cls).__name__ == "_Conditional"

def _ensure_iterable_conditions(conditionals):
    if callable(conditionals):
        return [conditionals]
    if isinstance(conditionals, (list, tuple)):
        if all(callable(f) for f in conditionals):
            return list(conditionals)
    raise TypeError("__conditionals__ must be a callable or a list/tuple of callables")
