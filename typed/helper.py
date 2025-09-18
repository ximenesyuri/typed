from typed.mods.decorators import typed
from typed.mods.types.base import Any, Bool, TYPE, Str, Set, List, Tuple, Dict, META, PARAMETRIC
from typed.mods.types.func import Function, Factory
from typed.mods.helper.helper import _name, _name_list
from typed.mods.helper.null import _null

@typed
def typeof(obj: Any) -> TYPE:
    return TYPE(obj)

@typed
def istype(obj: Any) -> Bool:
    return obj in TYPE

@typed
def issubtype(typ_1: TYPE, typ_2: TYPE) -> Bool:
    return typ_1 <= typ_2

@typed
def issame(typ_1: TYPE, typ_2: TYPE) -> Bool:
    return typ_1 is typ_2

@typed
def isequiv(typ_1: TYPE, typ2: TYPE) -> Bool:
    return typ_1 == typ_2

@typed
def isweaksubtype(typ_1: TYPE, typ_2: TYPE) -> Bool:
    return typ_1 << typ_2

@typed
def isweakequiv(typ_1: TYPE, typ_2: TYPE) -> Bool:
    return typ_1 ==~ typ_2

@typed
def isterm(obj: Any, typ: TYPE) -> Bool:
    return obj in typ

def declare(name, value=None):
    globals()[name] = value

@typed
def name(obj: Any) -> Str:
    return _name(obj)

@typed
def names(*objs: Tuple) -> Str:
    return _name_list(*objs)

null = _null

class new:
    @typed
    def meta(name: Str, meta_bases: Tuple(TYPE), instancecheck: Function, subclasscheck: Function=None) -> META:
        from typed.mods.helper.helper import _META
        return _META(name, meta_bases, instancecheck, subclasscheck)

    @typed
    def type(name: Str, meta_bases: Tuple(TYPE), instancecheck: Function, subclasscheck: Function=None, **attrs: Dict) -> TYPE:
        from typed.mods.types.base import Str
        if not isinstance(name, Str):
            raise TypeError
        meta_bases = tuple(TYPE(t) for t in bases)
        return _META(name.upper(), meta_bases, instancecheck, subclasscheck)(name, bases, attrs)

    @typed
    def parametric(*types: Tuple(TYPE), factory: Factory=None) -> PARAMETRIC:
        TYPES = (TYPE(typ) for typ in types)
        class _PARAMETRIC_(*TYPES):
            def __instancecheck__(cls, instance):
                return all(isinstance(instance, typ) for typ in types)
            def __subclasscheck__(cls, subclass):
                return all(issubclass(subclass, typ) for typ in types)
            def __call__(self, *args, **kwargs):
                if not args and not kwargs:
                    return self._type()
                elif args and isinstance(args[0], type):
                    return self._factory(*args, **kwargs)
                else:
                    return self._type(*args, **kwargs)

        class_name = _name(base_type)
        return _PARAMETRIC_(class_name, (base_type,), {
            "__display__": class_name,
            "base_type": base_type,
            "factory": factory
        })
