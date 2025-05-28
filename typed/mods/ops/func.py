from typed.mods.helper import (
    __flat,
    __hinted_domain,
    __hinted_codomain
)
from typed.mods.types_ import (
    HintedDomFuncType,
    HintedCodFuncType,
    HintedFuncType,
    TypedDomFuncType,
    TypedCodFuncType,
    TypedFuncType,
    BoolFuncType
)

def HintedDomainFunc(*domain_types):
    """
    Build the 'hinted-domain function type' of types:
        > the objects of 'HintedDomainFunc(X, Y, ...)'
        > are objects 'f(x: X, y: Y, ...)' of 'HintedDomFuncType'
    Flexible case:
        > objects of 'HintedDomFunc({X, Y, ...})'
        > are objects 'f(*args)' of 'HintedDomFunc'
        > whose arguments in the domain have type hints that
        > belong to 'Union(X, Y, ...)'
    """
    __flattypes, is_flexible = __flat(*domain_types)

    class __HintedDomainFunc(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, HintedDomFuncType):
                return False
            domain_hints = set(__hinted_domain(instance.func))
            if is_flexible:
                if not set(__flattypes).issubset(domain_hints):
                    return False
            else:
                if domain_hints != set(__flattypes):
                    return False
            return True

        def check(self, instance):
            if not callable(instance):
                return False
            domain_hints = set(__hinted_domain(instance))
            return set(domain_hints) == set(self.__types__)

    class_name = "HintedDomainFunc[" + (", ".join(t.__name__ for t in __flattypes)) + "]"
    return __HintedDomainFunc(class_name, (HintedDomFuncType,), {'__types__': __flattypes})

def HintedCodFunc(cod=None):
    """
    Build the 'hinted-codomain function type' of types:
        > the objects of hc__HintedFunc_type_(R) are
        > objects 'f(x, y, ... ) -> R' of HintedCodFuncType
    Flexible case:
        > objects of 'HintedCodFunc([R, S, ...])'
        > are objects 'f(*args)' of HintedCodFuncType
        > whose return type hint belong to 'coprod_(R, S, ...)'
    """
    class __HintedCodFunc(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, HintedCodFuncType):
                return False
            return_hint = __hinted_codomain(instance.func)
            return return_hint == cod

        def check(self, instance):
            if not callable(instance):
                return False
            return_hint = __hinted_codomain(instance)
            return return_hint == self.__codomain__

    class_name = f"HintedCodFunc[cod={cod.__name__}]"
    return __HintedCodFunc(class_name, (HintedCodFuncType,), {'__codomain__': cod})

def HintedFunc(*domain_types, cod=None):
    """
    Build the 'hinted function type' of types:
        > the objects of hfunc_type(X, Y, ..., cod=R)
        > are objects 'f(x: X, y: Y, ...) -> R' of HintedFuncType
    Flexible case:
        > objects of 'HintedFunc([X, Y, ...], cod=[R, S, ...])'
        > are objects 'f(*args)' of HintedFuncType
        > whose argument type hints belong to 'coprod_(X, Y, ...)'
        > and whose return type hint belongs to 'coprod_(R, S, ...)'
    """
    if cod is None:
        raise TypeError("Codomain type must be specified.")
    __flattypes, is_flexible = __flat(*domain_types)
    class __HintedFunc(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, HintedFuncType):
                return False
            domain_hints = set(__hinted_domain(instance.func))
            return_hint = __hinted_codomain(instance.func)
            if is_flexible:
                if not set(__flattypes).issubset(domain_hints):
                    return False
            else:
                if domain_hints != set(__flattypes):
                    return False
            return return_hint == cod

        def check(self, instance):
            if not callable(instance):
                return False
            domain_hints = set(__hinted_domain(instance))
            return_hint = __hinted_codomain(instance)
            return domain_hints == set(self.__types__) and return_hint == self.__codondomain__

    class_name = "HintedFunc[" + (", ".join(t.__name__ for t in __flattypes)) + f"]; cod={cod.__name__}"
    return __HintedFunc(class_name, (HintedFuncType,), {'__types__': __flattypes, '__codondomain__': cod})

def TypedDomFunc(*domain_types):
    """
    Build the 'typed-domain function type' of types:
        > the objects of 'TypedDomFunc(X, Y, ...)'
        > are objects 'f(x: X, y: Y, ...)' of 'TypedDomFuncType'
    Flexible case:
        > objects of 'TypedDomFunc([X, Y, ...])'
        > are objects 'f(*args)' of 'TypedDomFuncType'
        > whose arguments in the domain have type hints that
        > belong to 'coprod_(X, Y, ...)'
    """
    __flattypes, is_flexible = __flat(*domain_types)
    class __TypedDomFunc(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, TypedDomFuncType):
                return False
            domain_hints = set(__hinted_domain(instance.func))
            if is_flexible:
                if not set(__flattypes).issubset(domain_hints):
                    return False
            else:
                if domain_hints != set(__flattypes):
                    return False
            return True

        def check(self, instance):
            if not callable(instance):
                return False
            domain_hints = set(__hinted_domain(instance))
            return set(domain_hints) == set(self.__types__)

    class_name = f"TypedDomFunc([{', '.join(t.__name__ for t in __flattypes)}])"
    return __TypedDomFunc(class_name, (TypedDomFuncType,), {'__types__': __flattypes})


def TypedCodFunc(cod):
    """
    Build the 'typed-codomain function type' of types:
        > the objects of tc__HintedFunc_type_(R) are
        > objects 'f(x, y, ... ) -> R' of TypedCodFuncType
    Flexible case:
        > objects of 'TypedCodFunc([R, S, ...])'
        > are objects 'f(*args)' of TypedCodFuncType
        > whose return type hint belong to 'coprod_(R, S, ...)'
    """
    class __TypedCodFunc(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, TypedCodFuncType):
                return False
            return_hint = __hinted_codomain(instance.func)
            return return_hint == cod
        def check(self, instance):
            if not callable(instance):
                return False
            return_hint = __hinted_codomain(instance)
            return return_hint == self.__codomain__

    class_name = f"TypedCodFunc[cod={cod.__name__}]"
    return __TypedCodFunc(class_name, (TypedCodFuncType,), {'__codomain__': cod})


def TypedFunc(*domain_types, cod=None):
    if cod is None:
        raise TypeError("Codomain type must be specified.")

    __flattypes, is_flexible = __flat(*domain_types)
    class __TypedFunc(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, TypedFuncType):
                return False
            domain_hints = set(__hinted_domain(instance.func))
            return_hint = __hinted_codomain(instance.func)
            if is_flexible:
                if not set(__flattypes).issubset(domain_hints):
                    return False
            else:
                if domain_hints != set(__flattypes):
                    return False
            if return_hint != cod:
                return False
            return True

        def check(self, instance):
            if not callable(instance):
                return False
            domain_hints = set(__hinted_domain(instance))
            return_hint = __hinted_codomain(instance)
            return domain_hints == set(self.__types__) and return_hint == self.__codmondomain__

    class_name = f"TypedFunc([{', '.join(t.__name__ for t in __flattypes)}], cod={cod.__name__})"
    return __TypedFunc(class_name, (TypedFuncType,), {'__types__': __flattypes, '__codmondomain__': cod})

def BoolFunc(*domain_types):
    """
    Build the type of 'boolean functions' on a given type:
        > the objects of 'bfunc_(X, Y, ...)'  are
        > typed functions f(x: X, y: Y, ...) -> bool
    """
    __flattypes, is_flexible = __flat(*domain_types)

    class __BoolFunc(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, BoolFuncType):
                return False
            domain_hints = set(__hinted_domain(instance.func))
            return_hint = __hinted_codomain(instance.func)
            if is_flexible:
                if not set(__flattypes).issubset(domain_hints):
                    return False
            else:
                if domain_hints != set(__flattypes):
                    return False
            if return_hint != bool:
                return False
            return True

        def check(self, instance):
            if not callable(instance):
                return False
            domain_hints = set(__hinted_domain(instance))
            return_hint = __hinted_codomain(instance)
            return domain_hints == set(self.__types__) and return_hint == bool

    class_name = f"BoolFunc([{', '.join(t.__name__ for t in __flattypes)}])"
    return __BoolFunc(class_name, (BoolFuncType,), {'__types__': __flattypes})
