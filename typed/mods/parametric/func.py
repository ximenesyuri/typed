from functools import lru_cache as cache
from typed.mods.helper.helper import (
    _hinted_domain,
    _hinted_codomain,
    _get_num_args,
    _get_num_pos_args,
    _get_num_kwargs,
    _name,
    _name_list
)
from typed.mods.types.func import (
    Function,
    HintedDom,
    HintedCod,
    Hinted,
    TypedDom,
    TypedCod,
    Typed
)

@cache
def _Function_(*args):
    """
    Build the 'function type' of functions with
    a given number of argumens:
        > the objects of 'Function(n, m)' are functions
        > with exactly 'n>=0' pos arguments and 'm>=' kwargs.
        > For 'n<0' and 'm<0' any function is in 'Function(n, m)'
    """
    from typed.mods.types.base import TYPE
    class _FUNCTION(TYPE(Function)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Function):
                return False
            if len(args) == 1:
                if args[0] > 0:
                    return _get_num_args(instance) == args[0]
            if len(args) == 2:
                if args[0] < 0 and args[1] < 0:
                    return True
                if args[0] >= 0:
                    if args[1] >= 0:
                        return (
                            _get_num_pos_args(instance) == args[0] and
                            _get_num_kwargs(instance) == args[1]
                        )
                    return _get_num_pos_args(instance) == args[0]
                _get_num_kwargs(instance) == args[1]
            raise AttributeError(f"Expected 1 or 2 arguments. Received '{len(args)}' arguments")

    class_name = f'Function({args})'
    return _FUNCTION(class_name, (Function,), {'__display__': class_name})

@cache
def _HintedDom_(*types):
    """
    Build the 'hinted-domain function type' of types:
        > the objects of 'HintedDom(X, Y, ...)'
        > are objects 'f(x: X, y: Y, ...)' of 'HintedDom'
    The case 'HintedDom(n, m)' is the restriction of
    'Function(n, m)' to 'HintedDom'
    """

    from typed.mods.types.base import TYPE
    class _HINTED_DOM(TYPE(HintedDom)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, HintedDom):
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

    class_name = f"HintedDom({_name_list(*types)})"
    return _HINTED_DOM(class_name, (HintedDom,), {'__display__': class_name, '__types__': types})

@cache
def _HintedCod_(cod):
    """
    Build the 'hinted-codomain function type' of types:
        > the objects of 'HintedCod(R)' are
        > objects 'f(x, y, ... ) -> R' of 'HintedCod'
    """
    from typed.mods.types.base import TYPE
    class _HINTED_COD(TYPE(HintedCod)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, HintedCod):
                return False
            return_hint = _hinted_codomain(instance.func)
            return return_hint == cod

        def check(self, instance):
            if not callable(instance):
                return False
            return_hint = _hinted_codomain(instance)
            return return_hint == self.__codomain__

    class_name = f"HintedCod(cod={_name(cod)})"
    return _HINTED_COD(class_name, (HintedCod,), {"__display__": class_name, '__codomain__': cod})

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
def _TypedDom_(*types):
    """
    Build the 'typed-domain function type' of types:
        > the objects of 'TypedDom(X, Y, ...)'
        > are objects 'f(x: X, y: Y, ...)' of 'TypedDom'
    The case 'TypedDom(n, m)' is the restriction of
    'Function(n, m)' to 'TypedDom'
    """
    from typed.mods.types.base import TYPE
    class _TYPED_DOM(TYPE(TypedDom)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, TypedDom):
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

    class_name = f"TypedDom({_name_list(*types)})"
    return _TYPED_DOM(class_name, (TypedDom,), {"__display__": class_name, '__types__': types})

@cache
def _TypedCod_(cod):
    """
    Build the 'typed-codomain function type' of types:
        > the objects of TypedCod(R) are
        > objects 'f(x, y, ... ) -> R' of TypedCod
    """
    from typed.mods.types.base import TYPE
    class _TYPED_COD(TYPE(TypedCod)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, TypedCod):
                return False
            return_hint = _hinted_codomain(instance.func)
            return return_hint == cod
        def check(self, instance):
            if not callable(instance):
                return False
            return_hint = _hinted_codomain(instance)
            return return_hint == self.__codomain__

    class_name = f"TypedCod(cod={_name(cod)})"
    return _TYPED_COD(class_name, (TypedCod,), {"__display__": class_name, '__codomain__': typ})

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
