def _finite_instances_of(typ):
    if hasattr(typ, '__allowed_values__'):
        return set(typ.__allowed_values__)
    if hasattr(typ, '__types__'):
        vals = set()
        for t in typ.__types__:
            if hasattr(t, '__the_value__'):
                vals.add(t.__the_value__)
        if vals:
            return vals
    return None

def _equivalence(X, Y):
    xs = _finite_instances_of(X)
    ys = _finite_instances_of(Y)
    if xs is not None and ys is not None:
        return xs == ys
    return X is Y or (
        hasattr(X, "__types__")
        and hasattr(Y, "__types__")
        and getattr(X, "__types__", None) == getattr(Y, "__types__", None)
    )
