from builtins import type as __Type__
from typed.mods.meta.base import TYPE, UNIVERSE
from typed.mods.core import TYPESYSTEM, __UNIVERSE__, type, isterm, issub
from typed.mods.err import NotDefined, FuncErr, TypeSystemErr, TypeErr
from typed.helper.func import _unwrap

class CALLABLE(TYPE):
    """
    The universe of callables.

    type(CALLABLE)      is  UNIVERSE(1)
    isterm(T, CALLABLE) iff issub(type(T), CALLABLE)
    builtin(CALLABLE)   is  NotDefined
    null(CALLABLE)      is  TYPE.__null__
    """

    def __isterm__(typ, trm):
        from inspect import isbuiltin, ismethod, isfunction, isclass
        unwrapped = _unwrap(trm)

        return (
            isbuiltin(unwrapped)
            or ismethod(unwrapped)
            or isfunction(unwrapped)
            or isclass(unwrapped)
        )

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "CALLABLE"
    __builtin__ = NotDefined
    __null__    = TYPE.__null__

class CLASS(CALLABLE):
    """
    The universe of classes.

    type(CLASS)      is  UNIVERSE(1)
    isterm(T, CLASS) iff issub(type(T), CLASS)
    """

    def __isterm__(typ, trm):
        from inspect import isclass

        unwrapped = _unwrap(trm)
        if issub(type(trm), typ) or issub(type(unwrapped), typ):
            return True

        return isclass(_unwrap(trm))

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "CLASS"
    __builtin__ = NotDefined
    __null__    = TYPE.__null__

class METHOD(CALLABLE):
    """
    The universe of methods.
    """

    is_meta = True
    def __isterm__(typ, trm):
        from inspect import ismethod

        unwrapped = _unwrap(trm)
        if issub(type(trm), typ) or issub(type(unwrapped), typ):
            return True

        return ismethod(_unwrap(trm))

    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "METHOD"
    __builtin__ = NotDefined
    __null__    = TYPE.__null__

class BOUND_METHOD(METHOD):
    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "BOUND_METHOD"
    __builtin__ = NotDefined
    __null__    = TYPE.__null__

class UNBOUND_METHOD(METHOD):
    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "UNBOUND_METHOD"
    __builtin__ = NotDefined
    __null__    = TYPE.__null__

class BUILTIN_FUNC(CALLABLE):
    """
    The universe of built-in functions.
    """

    is_meta = True
    def __isterm__(typ, trm):
        from inspect import isbuiltin

        unwrapped = _unwrap(trm)
        if issub(type(trm), typ) or issub(type(unwrapped), typ):
            return True

        return isbuiltin(unwrapped)

    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "BUILTIN_FUNC"
    __builtin__ = NotDefined
    __null__    = TYPE.__null__

class LAMBDA(CALLABLE):
    """
    The universe of lambdas.
    """

    is_meta = True
    def __isterm__(typ, trm):
        from inspect import isfunction

        unwrapped = _unwrap(trm)
        if issub(type(trm), typ) or issub(type(unwrapped), typ):
            return True

        return isfunction(unwrapped) and unwrapped.__name__ == "<lambda>"

    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "LAMBDA"
    __builtin__ = NotDefined
    __null__    = TYPE.__null__

class GENERATOR(TYPE):
    def __isterm__(typ, trm):
        if not super().__isterm__(trm): return False
        if issub(type(trm), typ): return True

        from inspect import isgeneratorfunction, isasyncgenfunction

        return (
            isgeneratorfunction(trm)
            or isasyncgenfunction(trm)
        )

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "GENERATOR"
    __builtin__ = NotDefined
    __null__    = TYPE.__null__

class FUNC(CALLABLE):
    """
    The metatype of functions.
    """
    def __isterm__(typ, trm):
        from typed.helper.func import _unwrap
        from inspect import isfunction, ismethod, isbuiltin

        unwrapped = _unwrap(trm)
        if issub(type(trm), typ) or issub(type(unwrapped), typ):
            return True

        return (
            isfunction(unwrapped)
            and unwrapped.__name__ != "<lambda>"
            and not ismethod(unwrapped)
            and not isbuiltin(unwrapped)
        )

    def __call__(typ, *args, typesystem=NotDefined, **kwargs):
        if typesystem is NotDefined:
            typesystem = TYPESYSTEM

        if len(args) == 1:
            func = args[0]
            if not issub(type(func), CALLABLE):
                raise TypeErr(
                    term=typ,
                    args=func,
                    received=type(func),
                    expected=typ
                )
            return __UNIVERSE__.__call__(typ, args[0])

        if args or kwargs:
            raise FuncErr(
                details="received unexpected number of arguments",
                expected=1,
                received=len(args)
            )

        return typ

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "FUNC"
    __builtin__ = NotDefined
    __null__ = NotDefined

class PARTIAL(FUNC):
    def __isterm__(typ, trm):
        return super().__isterm__(trm) and getattr(trm, 'is_partial', False)

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "PARTIAL"
    __builtin__ = NotDefined
    __null__ = NotDefined

class DOM_FUNC(FUNC):
    """
    The metatype of domain-specified functions.
    """
    def __isterm__(typ, trm):
        if not super().__isterm__(trm):
            return False

        dom = getattr(trm, "dom", NotDefined) or getattr(trm, "domain", NotDefined)
        if dom is NotDefined:
            return False

        dom_type = getattr(typ, "__types__", NotDefined)
        if dom_type is NotDefined:
            return False

        try:
            actual = tuple(dom)
        except TypeError:
            actual = (dom,)

        return actual == dom_type

    def __call__(typ, *args, typesystem=None, **kwargs):
        from typed.mods.core import names
        from typed.mods.core import TYPESYSTEM
        if typesystem is None:
            typesystem = TYPESYSTEM

        if kwargs:
            raise FuncErr(
                details="function do not expect kwargs",
                func=typ
            )

        if not args: return typ

        if len(args) == 1:
            func = args[0]
            if not issub(type(func), FUNC):
                raise TypeErr(
                    term=func,
                    received=type(func),
                    expected=FUNC
                )

            return __UNIVERSE__.__call__(typ, func)

        types = tuple(args)

        if all(isinstance(t, __Type__) for t in types):
            if typesystem.is_restrictive:
                for t in types:
                    if t not in tuple(typesystem.__members__.values()):
                        raise TypeSystemErr(
                            type=t,
                            typesystem=typesystem
                        )

            name = f"DomFunc({names(*types)})"
            return FUNC(name, (typ,), {
                "__display__": name,
                "__types__": types,
                "__typesystems__": [typesystem],
                "is_type": True
            })

        for t in types:
            wrong = [t for t in types if not isinstance(t, __Type__)]

        raise TypeErr(
            term=typ,
            args=tuple(wrong),
            received=tuple([type(t) for t in types]),
            expected=tuple([TYPE for t in types])
        )

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "DOM_FUNC"
    __builtin__ = NotDefined
    __null__ = NotDefined

class COD_FUNC(FUNC):
    """
    The metatype of codomain-specified functions.
    """
    def __isterm__(typ, trm):
        if not super().__isterm__(trm):
            return False

        cod = getattr(trm, "cod", NotDefined) or getattr(trm, "codomain", NotDefined)
        if cod is NotDefined:
            return False

        cod_type = getattr(typ, "__types__", NotDefined)
        if cod_type is NotDefined:
            return False

        return cod in tuple(cod_type)

    def __call__(typ, *args, cod=None, typesystem=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.helper.general import _name
        from typed.mods.core import TYPESYSTEM
        
        if typesystem is None:
            typesystem = TYPESYSTEM

        if "cod" in kwargs:
            cod = kwargs.pop("cod")

        if len(args) == 1 and callable(args[0]) and cod is None and not kwargs:
            return __Type__.__call__(typ, args[0])
            
        if cod is None and len(args) == 1 and isterm(args[0], TYPE):
            cod = args[0]
            args = ()

        if cod is None and not args and not kwargs:
            return typ

        if isinstance(cod, __Type__) and not args and not kwargs:
            if typesystem.is_restrictive:
                if cod not in tuple(typesystem.__members__.values()):
                    raise TypeError(f"Type {cod} not in typesystem.__types__")
    
            class_name = f"CodFunc({_name(cod)})"
            return __Type__.__new__(typ.__class__, class_name, (typ,), {
                "__display__": class_name,
                "__codomain__": cod,
                "__typesystems__": [typesystem],
                "is_type": True
            })

        raise TypeError("CodFunc(X) expects a single TYPE argument")

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "COD_FUNC"
    __builtin__ = NotDefined
    __null__ = NotDefined

class COMP_FUNC(DOM_FUNC, COD_FUNC):
    """
    The metatype of composable functions.
    """
    def __isterm__(typ, trm):
        from typed.mods.types.func import DomFunc, CodFunc

        if not isterm(trm, DomFunc):
            return False
        if not isterm(trm, CodFunc):
            return False

        dom_types = getattr(typ, "__types__", None)
        cod_type = getattr(typ, "__codomain__", None)

        if dom_types is not None:
            dom = getattr(trm, "dom", getattr(trm, "domain", None))
            try:
                actual_dom = tuple(dom)
            except TypeError:
                actual_dom = (dom,)
            if actual_dom != dom_types:
                return False

        if cod_type is not None:
            cod = getattr(trm, "cod", getattr(trm, "codomain", None))
            if cod is not cod_type:
                return False

        return True

    def __call__(typ, *args, cod=None, typesystem=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.helper.general import _name_list, _name
        from typed.mods.core import TYPESYSTEM

        if typesystem is None:
            typesystem = TYPESYSTEM
            
        if "cod" in kwargs:
            cod = kwargs.pop("cod")

        if len(args) == 1 and callable(args[0]) and cod is None and not kwargs:
            return __Type__.__call__(typ, args[0])

        if not args and cod is None and not kwargs:
            return typ

        if args and all(isterm(t, TYPE) for t in args) and isterm(cod, TYPE) and not kwargs:
            types = tuple(args)
            if typesystem.is_restrictive:
                for t in types:
                    if t not in typesystem.__types__:
                        raise TypeError(f"Type {t} not in typesystem.__types__")
                if cod not in typesystem.__types__:
                    raise TypeError(f"Type {cod} not in typesystem.__types__")

            class_name = f"CompFunc({_name_list(*types)}, cod={_name(cod)})"
            return __Type__.__new__(typ.__class__, class_name, (typ,), {
                "__display__": class_name,
                "__types__": types,
                "__codomain__": cod,
                "__typesystems__": [typesystem],
                "is_type": True
            })

        raise TypeError("CompFunc(X, Y, ..., cod=Z) expects TYPE arguments only")

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "COMP_FUNC"
    __builtin__ = NotDefined
    __null__ = NotDefined


class DOM_HINTED(DOM_FUNC, PARTIAL):
    """
    Metatype for DomHinted.
    """
    def __isterm__(typ, trm):
        if issubclass(type(trm), typ):
            return True
        if not super().__isterm__(trm):
            return False
        from typed.mods.helper.func import _is_domain_hinted, _hinted_domain
        try:
            if not _is_domain_hinted(trm.func):
                return False
        except Exception:
            return False
            
        expected = getattr(typ, "__types__", None)
        if expected is not None:
            domain_hints = set(_hinted_domain(trm.func))
            return domain_hints == set(expected)
            
        return True

    def __call__(typ, *args, typesystem=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.helper.general import _name_list
        from typed.mods.core import TYPESYSTEM
        
        if typesystem is None:
            typesystem = TYPESYSTEM
            
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return __Type__.__call__(typ, args[0])

        if not args and not kwargs:
            return typ

        if args and all(isterm(t, TYPE) for t in args) and not kwargs:
            types = tuple(args)
            if typesystem.is_restrictive:
                for t in types:
                    if t not in typesystem.__types__:
                        raise TypeError(f"Type {t} not in typesystem.__types__")
            
            class_name = f"DomHinted({_name_list(*types)})"

            return __Type__.__new__(typ.__class__, class_name, (typ,), {
                "__display__": class_name,
                "__types__": types,
                "__typesystems__": [typesystem],
                "is_type": True
            })

        raise TypeError(f"{typ.__name__}(): expected 0 args, or a callable, or TYPE arguments")
        
    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "DOM_HINTED"
    __builtin__ = NotDefined
    __null__ = NotDefined

class COD_HINTED(COD_FUNC, PARTIAL):
    """
    Metatype for CodHinted.
    """
    def __isterm__(typ, trm):
        from typed.mods.types.base import TYPE
        from typed.mods.helper.func import _is_codomain_hinted, _hinted_codomain

        if issub(TYPE(trm), typ):
            return True
        if not super().__isterm__(trm):
            return False
        try:
            if not _is_codomain_hinted(trm.func):
                return False
        except Exception:
            return False
            
        expected = getattr(typ, "__codomain__", None)
        if expected is not None:
            return_hint = _hinted_codomain(trm.func)
            return return_hint == expected
            
        return True

    def __call__(typ, *args, cod=None, typesystem=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.helper.general import _name
        from typed.mods.core import TYPESYSTEM
        
        if typesystem is None:
            typesystem = TYPESYSTEM
            
        if "cod" in kwargs:
            cod = kwargs.pop("cod")

        if len(args) == 1 and callable(args[0]) and cod is None and not kwargs:
            return __Type__.__call__(typ, args[0])
            
        if cod is None and len(args) == 1 and isterm(args[0], TYPE):
            cod = args[0]
            args = ()

        if cod is None and not args and not kwargs:
            return typ

        if isterm(cod, TYPE) and not args and not kwargs:
            if typesystem.is_restrictive:
                if cod not in typesystem.__types__:
                    raise TypeError(f"Type {cod} not in typesystem.__types__")
                    
            class_name = f"CodHinted(cod={_name(cod)})"

            return __Type__.__new__(typ.__class__, class_name, (typ,), {
                "__display__": class_name,
                "__codomain__": cod,
                "__typesystems__": [typesystem],
                "is_type": True
            })

        raise TypeError(f"{typ.__name__}(): expected 0 args, or a callable, or a single TYPE")
        
    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "COD_HINTED"
    __builtin__ = NotDefined
    __null__ = NotDefined


class HINTED(COMP_FUNC, COD_HINTED, DOM_HINTED):
    """
    Metatype for Hinted.
    """
    def __isterm__(typ, trm):
        if not super().__isterm__(trm):
            return False
        from typed.mods.helper.func import _hinted_domain, _hinted_codomain
        
        expected_types = getattr(typ, "__types__", None)
        expected_cod = getattr(typ, "__codomain__", None)
        
        if expected_types is not None:
            domain_hints = set(_hinted_domain(trm.func))
            if domain_hints != set(expected_types):
                return False
                
        if expected_cod is not None:
            return_hint = _hinted_codomain(trm.func)
            if return_hint != expected_cod:
                return False
                
        return True

    def __call__(typ, *args, cod=None, typesystem=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.helper.general import _name_list, _name
        from typed.mods.core import TYPESYSTEM

        if typesystem is None:
            typesystem = TYPESYSTEM
            
        if "cod" in kwargs:
            cod = kwargs.pop("cod")

        if len(args) == 1 and callable(args[0]) and cod is None and not kwargs:
            return __Type__.__call__(typ, args[0])

        if not args and cod is None and not kwargs:
            return typ

        if args and all(isterm(t, TYPE) for t in args) and isterm(cod, TYPE) and not kwargs:
            types = tuple(args)
            if typesystem.is_restrictive:
                for t in types:
                    if t not in typesystem.__types__:
                        raise TypeError(f"Type {t} not in typesystem.__types__")
                if cod not in typesystem.__types__:
                    raise TypeError(f"Type {cod} not in typesystem.__types__")

            class_name = f"Hinted({_name_list(*types)}; {_name(cod)})"
            return __Type__.__new__(typ.__class__, class_name, (typ,), {
                "__display__": class_name,
                "__types__": types,
                "__codomain__": cod,
                "__typesystems__": [typesystem],
                "is_type": True
            })

        raise TypeError(f"{typ.__name__}(): expected 0 args, or a callable, or TYPE arguments plus cod=TYPE")

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "HINTED"
    __builtin__ = NotDefined
    __null__ = NotDefined


class DOM_TYPED(DOM_HINTED):
    """
    Metatype for DomTyped.
    """
    def __isterm__(typ, trm):
        if not super().__isterm__(trm):
            return False
        expected = getattr(typ, "__types__", None)
        if expected is not None:
            from typed.mods.helper.func import _hinted_domain
            domain_hints = set(_hinted_domain(trm.func))
            return domain_hints == set(expected)
        return True

    def __call__(typ, *args, typesystem=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.helper.general import _name_list
        from typed.mods.core import TYPESYSTEM
        
        if typesystem is None:
            typesystem = TYPESYSTEM

        if len(args) == 1 and callable(args[0]) and not kwargs:
            return __Type__.__call__(typ, args[0])

        if not args and not kwargs:
            return typ

        if args and all(isterm(t, TYPE) for t in args) and not kwargs:
            types = tuple(args)
            if typesystem.is_restrictive:
                for t in types:
                    if t not in typesystem.__types__:
                        raise TypeError(f"Type {t} not in typesystem.__types__")
            
            class_name = f"DomTyped({_name_list(*types)})"

            return __Type__.__new__(typ.__class__, class_name, (typ,), {
                "__display__": class_name,
                "__types__": types,
                "__typesystems__": [typesystem],
                "is_type": True
            })

        raise TypeError(f"{typ.__name__}(): expected 0 args, or a callable, or TYPE arguments")

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "DOM_TYPED"
    __builtin__ = NotDefined
    __null__ = NotDefined


class COD_TYPED(COD_HINTED):
    """
    Metatype for CodTyped.
    """
    def __isterm__(typ, trm):
        if not super().__isterm__(trm):
            return False
        expected = getattr(typ, "__codomain__", None)
        if expected is not None:
            from typed.mods.helper.func import _hinted_codomain
            return_hint = _hinted_codomain(trm.func)
            return return_hint == expected
        return True

    def __call__(typ, *args, cod=None, typesystem=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.helper.general import _name
        from typed.mods.core import TYPESYSTEM
        
        if typesystem is None:
            typesystem = TYPESYSTEM
            
        if "cod" in kwargs:
            cod = kwargs.pop("cod")

        if len(args) == 1 and callable(args[0]) and cod is None and not kwargs:
            return __Type__.__call__(typ, args[0])
            
        if cod is None and len(args) == 1 and isterm(args[0], TYPE):
            cod = args[0]
            args = ()

        if cod is None and not args and not kwargs:
            return typ

        if isterm(cod, TYPE) and not args and not kwargs:
            if typesystem.is_restrictive:
                if cod not in typesystem.__types__:
                    raise TypeError(f"Type {cod} not in typesystem.__types__")
                    
            class_name = f"CodTyped(cod={_name(cod)})"

            return __Type__.__new__(typ.__class__, class_name, (typ,), {
                "__display__": class_name,
                "__codomain__": cod,
                "__typesystems__": [typesystem],
                "is_type": True
            })

        raise TypeError(f"{typ.__name__}(): expected 0 args, or a callable, or a single TYPE")

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "COD_TYPED"
    __builtin__ = NotDefined
    __null__ = NotDefined


class TYPED(HINTED, DOM_TYPED, COD_TYPED):
    """
    Metatype for Typed.
    """
    def __isterm__(typ, trm):
        if getattr(trm, 'is_partial', False):
            orig = getattr(trm, 'original_func', None)
            if orig is None:
                return False

            if getattr(orig, 'is_lazy', False):
                return False

            return isterm(orig, typ)

        if getattr(trm, "is_lazy", False):
            return False

        if not super().__isterm__(trm):
            return False
            
        expected_types = getattr(typ, "__types__", None)
        expected_cod = getattr(typ, "__codomain__", None)
        
        if expected_types is not None or expected_cod is not None:
            from typed.mods.helper.func import _hinted_domain, _hinted_codomain
            from typed.mods.types.base import Any
            
            if expected_types is not None:
                domain_hints = set(_hinted_domain(trm.func))
                if len(expected_types) == 1 and expected_types[0] is Any:
                    pass
                elif domain_hints != set(expected_types):
                    return False
                    
            if expected_cod is not None:
                return_hint = _hinted_codomain(trm.func)
                if return_hint != expected_cod:
                    return False

        return True

    def __call__(typ, *args, cod=None, typesystem=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.helper.general import _name_list, _name
        from typed.mods.core import TYPESYSTEM

        if typesystem is None:
            typesystem = TYPESYSTEM

        if "cod" in kwargs:
            cod = kwargs.pop("cod")

        if len(args) == 1 and callable(args[0]) and cod is None and not kwargs:
            return __Type__.__call__(typ, args[0])

        if not args and cod is None and not kwargs:
            return typ

        if cod is not None and all(isterm(t, TYPE) for t in args):
            types = tuple(args)
            if typesystem.is_restrictive:
                for t in types:
                    if t not in typesystem.__types__:
                        raise TypeError(f"Type {t} not in typesystem.__types__")
                if cod not in typesystem.__types__:
                    raise TypeError(f"Type {cod} not in typesystem.__types__")

            class_name = f"Typed({_name_list(*types)}, cod={_name(cod)})"
            return __Type__.__new__(typ.__class__, class_name, (typ,), {
                "__display__": class_name,
                "__types__": types,
                "__codomain__": cod,
                "__typesystems__": [typesystem],
                "is_type": True
            })

        raise TypeError("Typed() expects a callable, or TYPE arguments plus cod=TYPE")

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "TYPED"
    __builtin__ = NotDefined
    __null__ = NotDefined


class CONDITION(TYPED):
    def __isterm__(typ, trm):
        from typed.mods.types.base import Bool
        return super().__isterm__(trm) and getattr(trm, "cod", None) is Bool

    def __call__(typ, *args, typesystem=None, **kwargs):
        from typed.mods.types.base import TYPE, Bool
        from typed.mods.helper.general import _name_list, _name
        from typed.mods.core import TYPESYSTEM

        if typesystem is None:
            typesystem = TYPESYSTEM

        if len(args) == 1 and callable(args[0]) and not kwargs:
            instance = __Type__.__call__(typ, args[0])
            if getattr(instance, "cod", None) is not Bool:
                raise TypeError(
                    f"Wrong type in codomain of '{_name(args[0])}':\n"
                    f" ==> '{_name(getattr(instance, 'cod', None))}' is not 'Bool'"
                )
            return instance

        if not args and not kwargs:
            return typ

        if args and all(isterm(t, TYPE) for t in args) and not kwargs:
            types = tuple(args)
            if typesystem.is_restrictive:
                for t in types:
                    if t not in typesystem.__types__:
                        raise TypeError(f"Type {t} not in typesystem.__types__")

            class_name = f"Condition({_name_list(*types)})"
            return __Type__.__new__(typ.__class__, class_name, (typ,), {
                "__display__": class_name,
                "__types__": types,
                "__codomain__": Bool,
                "__typesystems__": [typesystem],
                "is_type": True
            })

        raise TypeError("Condition() expects a Bool-returning callable, or TYPE arguments")

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "CONDITION"
    __builtin__ = NotDefined
    __null__ = NotDefined


class FACTORY(TYPED):
    def __isterm__(typ, trm):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import Typed
        if trm == Typed.__call__:
            return True
        return isterm(trm, Typed) and issub(trm.cod, TYPE)

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "FACTORY"
    __builtin__ = NotDefined
    __null__ = NotDefined

class OPERATION(FACTORY):
    def __isterm__(typ, trm):
        from typed.mods.types.base import TYPE, Tuple
        return super().__isterm__(trm) and issub(trm.dom, Tuple(TYPE))

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "OPERATION"
    __builtin__ = NotDefined
    __null__ = NotDefined

class DEPENDENT(FACTORY):
    def __isterm__(typ, trm):
        if super().__isterm__(trm) and hasattr(trm, "is_dependent_type"):
            return trm.is_dependent_type
        return False

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "DEPENDENT"
    __builtin__ = NotDefined
    __null__ = NotDefined

class LAZY(HINTED):
    def __isterm__(typ, trm):
        if getattr(trm, "is_partial", False):
            orig = getattr(trm, "original_func", None)
            if orig is not None:
                return isterm(orig, typ)
            return False

        if getattr(trm, "is_lazy", False):
            return True

        return False

    def __call__(typ, *args, typesystem=None, **kwargs):
        from typed.mods.core import TYPESYSTEM
        
        if typesystem is None:
            typesystem = TYPESYSTEM
            
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return __Type__.__call__(typ, args[0])

        return super().__call__(*args, **kwargs)

    is_meta = True
    __typesystems__ = [TYPESYSTEM]
    __type__ = UNIVERSE(1)
    __display__ = "LAZY"
    __builtin__ = NotDefined
    __null__ = NotDefined
