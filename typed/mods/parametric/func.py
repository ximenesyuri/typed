from functools import lru_cache as cache
from typed.mods.helper.func import (
    _hinted_domain,
    _hinted_codomain,
)
from typed.mods.helper.general import _name, _name_list
from typed.mods.types.func import (
    DomHinted,
    CodHinted,
    Hinted,
    DomTyped,
    CodTyped,
    Typed
)

@cache
def _DomHinted_(*types):
    """
    Build the 'hinted-domain function type' of types:
        > the objects of 'DomHinted(X, Y, ...)'
        > are objects 'f(x: X, y: Y, ...)' of 'DomHinted'
    The case 'DomHinted(n, m)' is the restriction of
    'Function(n, m)' to 'DomHinted'
    """

    from typed.mods.types.base import TYPE
    class _HINTED_DOM(TYPE(DomHinted)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, DomHinted):
                return False
            domain_hints = set(_hinted_domain(instance.func))
            if domain_hints != set(types):
                return False
            return True

        def check(self, instance):
            if not callable(instance):
                return False
            domain_hints = set(_hinted_domain(instance))
            return set(domain_hints) == set(self.__types__)

    class_name = f"DomHinted({_name_list(*types)})"
    return _HINTED_DOM(class_name, (DomHinted,), {'__display__': class_name, '__types__': types})

@cache
def _CodHinted_(cod):
    """
    Build the 'hinted-codomain function type' of types:
        > the objects of 'CodHinted(R)' are
        > objects 'f(x, y, ... ) -> R' of 'CodHinted'
    """
    from typed.mods.types.base import TYPE
    class _HINTED_COD(TYPE(CodHinted)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, CodHinted):
                return False
            return_hint = _hinted_codomain(instance.func)
            return return_hint == cod

        def check(self, instance):
            if not callable(instance):
                return False
            return_hint = _hinted_codomain(instance)
            return return_hint == self.__codomain__

    class_name = f"CodHinted(cod={_name(cod)})"
    return _HINTED_COD(class_name, (CodHinted,), {"__display__": class_name, '__codomain__': cod})

@cache
def _Hinted_(*types, cod):
    """
    Build the 'hinted function type' of types:
        > the objects of Hinted(X, Y, ..., cod=R)
        > are objects 'f(x: X, y: Y, ...) -> R' of Hinted
    The case 'Hinted(n, m)' is the restriction of
    'Function(n, m)' to 'Hinted'
    """
    from typed.mods.types.base import TYPE
    class _HINTED(TYPE(Hinted)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Hinted):
                return False
            domain_hints = set(_hinted_domain(instance.func))
            return_hint = _hinted_codomain(instance.func)
            if domain_hints != set(types):
                return False
            return return_hint == cod

        def check(self, instance):
            if not callable(instance):
                return False
            domain_hints = set(_hinted_domain(instance))
            return_hint = _hinted_codomain(instance)
            return domain_hints == set(self.__types__) and return_hint == self.__coddomain__

    class_name = f"Hinted({_name_list(*types)}; {_name(cod)})"
    return _HINTED(class_name, (Hinted,), {"__display__": class_name, '__types__': types, '__codomain__': cod})

@cache
def _DomTyped_(*types):
    """
    Build the 'typed-domain function type' of types:
        > the objects of 'DomTyped(X, Y, ...)'
        > are objects 'f(x: X, y: Y, ...)' of 'DomTyped'
    The case 'DomTyped(n, m)' is the restriction of
    'Function(n, m)' to 'DomTyped'
    """
    from typed.mods.types.base import TYPE
    class _TYPED_DOM(TYPE(DomTyped)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, DomTyped):
                return False
            domain_hints = set(_hinted_domain(instance.func))
            if domain_hints != set(types):
                return False
            return True

        def check(self, instance):
            if not callable(instance):
                return False
            domain_hints = set(_hinted_domain(instance))
            return set(domain_hints) == set(self.__types__)

    class_name = f"DomTyped({_name_list(*types)})"
    return _TYPED_DOM(class_name, (DomTyped,), {"__display__": class_name, '__types__': types})

@cache
def _CodTyped_(cod):
    """
    Build the 'typed-codomain function type' of types:
        > the objects of CodTyped(R) are
        > objects 'f(x, y, ... ) -> R' of CodTyped
    """
    from typed.mods.types.base import TYPE
    class _TYPED_COD(TYPE(CodTyped)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, CodTyped):
                return False
            return_hint = _hinted_codomain(instance.func)
            return return_hint == cod
        def check(self, instance):
            if not callable(instance):
                return False
            return_hint = _hinted_codomain(instance)
            return return_hint == self.__codomain__

    class_name = f"CodTyped(cod={_name(cod)})"
    return _TYPED_COD(class_name, (CodTyped,), {"__display__": class_name, '__codomain__': typ})

@cache
def _Typed_(*types, cod=None):
    """
    Build the type of 'typed functions' with given types:
        > the objects of 'Typed(X, Y, ..., cod=K)' are
        > typed functions f(x: X, y: Y, ...) -> K
    The case 'Typed(n, m)' is the restriction of
    'Function(n, m)' to 'Typed'
    """
    from typed.mods.types.base import TYPE
    class _TYPED(TYPE(Typed)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Typed):
                return False
            domain_hints = set(_hinted_domain(instance.func))
            return_hint = _hinted_codomain(instance.func)
            from typed.mods.types.base import Any
            if len(types) == 1 and types[0] is Any:
                if return_hint == cod:
                    return True
            if domain_hints != set(types):
                return False
            if return_hint != cod:
                return False
            return True

        def check(self, instance):
            if not callable(instance):
                return False
            domain_hints = set(_hinted_domain(instance))
            return_hint = _hinted_codomain(instance)
            return domain_hints == set(self.__types__) and return_hint == self.__codomain___

    class_name = f"Typed({_name_list(*types)}, cod={_name(cod)})"
    return _TYPED(class_name, (Typed,), {"__display__": class_name, '__types__': types, '__codomain__': cod})

@cache
def _Condition_(*types):
    return _Typed_(*types, cod=bool)
