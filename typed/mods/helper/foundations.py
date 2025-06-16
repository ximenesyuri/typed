from typed.mods.factories.func import TypedFunc
from typed.mods.helper.helper import _get_type_display_name

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

class __CAT(type):
    """
    Metaclass for category objects.

    An object (Obj, Morp) is an instance of CAT IF:
    - Obj is a type
    - Morp is a subclass of TypedFuncType produced by e.g. TypedFunc(Obj, cod=Obj)
    - All morphisms in Morp have domain and codomain exactly Obj
    """
    def __instancecheck__(self, x):
        if not (isinstance(x, tuple) and len(x) == 2):
            return False
        obj, morp = x
        if not isinstance(obj, type):
            return False
        canon = TypedFunc(obj, cod=obj)
        return isinstance(morp, type) and issubclass(morp, canon)

    def __call__(self, obj, morp):
        if not isinstance((obj, morp), self):
            raise TypeError(
                f"({_get_type_display_name(obj)}, {_get_type_display_name(morp)}): is not a category object.\n"
                f" ==> 'Morp={morp.__name__}' should be a subtype of 'TypedFunc(Obj, cod=Obj)'."
            )
        return (obj, morp)
