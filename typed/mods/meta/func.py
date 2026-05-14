from typed.mods.meta.base import TYPE, UNIVERSE
from typed.mods.core import TYPESYSTEM, type, term, sub
from typed.mods.err import NotDefined

class CALLABLE(TYPE):
    """
    The universe of callables.

    type(CALLABLE)    is  UNIVERSE(1)
    term(T, CALLABLE) iff sub(type(T), CALLABLE)
    builtin(CALLABLE) is  NotDefined
    null(CALLABLE)    is  TYPE.__null__
    """

    def __term__(typ, trm):
        if not super().__term__(trm): return False
        if sub(type(trm), typ): return True

        from typed.helper.func import _unwrap
        from inspect import isbuiltin, ismethod, isfunction, isclass
        unwrapped = _unwrap(trm)

        return (
            isbuiltin(unwrapped)
            or ismethod(unwrapped)
            or isfunction(unwrapped)
            or isclass(unwrapped)
        )

    __typesystem__ = TYPESYSTEM
    __type__ = UNIVERSE(1)
    __display__ = "CALLABLE"
    __builtin__ = NotDefined
    __null__    = TYPE.__null__

class GENERATOR(TYPE):
    def __term__(typ, trm):
        if not super().__term__(trm): return False
        if sub(type(trm), typ): return True

        from inspect import isgeneratorfunction, isasyncgenfunction

        return (
            isgeneratorfunction(trm)
            or isasyncgenfunction(trm)
        )

class FUNC(CALLABLE):
    def __term__(typ, trm):
        if sub(type(trm), typ): return True
        if not super().__term__(trm): return False

        unwrapped = _unwrap(trm)

        if sub(type(trm), typ) or sub(type(unwrapped), typ):
            return True
        return (
            isfunction(unwrapped)
            and unwrapped.__name__ != "<lambda>"
            and not ismethod(unwrapped)
            and not isbuiltin(unwrapped)
        )

    def __call__(typ, *call_args, **call_kwargs):
        if len(call_args) > 1:
            raise TypeError(
                "Function(): expected at most one positional argument (a callable), "
                f"got {len(call_args)}"
            )

        allowed_kw = {"args", "posargs", "kwargs"}
        unexpected = set(call_kwargs) - allowed_kw
        if unexpected:
            raise TypeError(
                "Function(): unexpected keyword arguments: "
                + ", ".join(sorted(unexpected))
            )

        f = call_args[0] if call_args else None

        arg_count = call_kwargs.get("args", -1)
        pos_count = call_kwargs.get("posargs", -1)
        kw_count = call_kwargs.get("kwargs", -1)

        from typed.mods.types.base import TYPE

        for name, value in (("args", arg_count), ("posargs", pos_count), ("kwargs", kw_count)):
            if not term(value, int):
                raise TypeError(
                    "Wrong type in 'Function' call:\n"
                    f" ==> '{_name(value)}': has unexpected type for parameter '{name}'\n"
                    "     [expected_type] Int\n"
                    f"     [received_type] '{_name(TYPE(value))}'"
                )

        if f is not None:
            if not callable(f):
                raise TypeError(
                    "Wrong type in 'Function' call:\n"
                    f" ==> '{_name(f)}': first argument is not callable\n"
                    "     [expected_type] callable\n"
                    f"     [received_type] '{_name(TYPE(f))}'"
                )

            if any(v >= 0 for v in (arg_count, pos_count, kw_count)):
                target = _unwrap(f)

                if arg_count >= 0:
                    got = _get_num_args(target)
                    if got != arg_count:
                        raise TypeError(
                            f"Function(): callable '{_name(f)}' has wrong total number of arguments\n"
                            f"     [expected args] {arg_count}\n"
                            f"     [received args] {got}"
                        )

                if pos_count >= 0:
                    got = _get_num_posargs(target)
                    if got != pos_count:
                        raise TypeError(
                            f"Function(): callable '{_name(f)}' has wrong number of positional arguments\n"
                            f"     [expected posargs] {pos_count}\n"
                            f"     [received posargs] {got}"
                        )

                if kw_count >= 0:
                    got = _get_num_kwargs(target)
                    if got != kw_count:
                        raise TypeError(
                            f"Function(): callable '{_name(f)}' has wrong number of keyword arguments\n"
                            f"     [expected kwargs] {kw_count}\n"
                            f"     [received kwargs] {got}"
                        )

            return type.__call__(typ, f, arg_count, pos_count, kw_count)

        if arg_count < 0 and pos_count < 0 and kw_count < 0:
            return typ

        from typed.mods.types.func import Function

        parts = []
        if arg_count >= 0:
            parts.append(f"args={arg_count}")
        if pos_count >= 0:
            parts.append(f"posargs={pos_count}")
        if kw_count >= 0:
            parts.append(f"kwargs={kw_count}")
        inside = ", ".join(parts)
        class_name = f"Function({inside})" if inside else "Function()"

        return FUNC(
            class_name,
            (Function,),
            {
                "__display__": class_name,
                "__expected_args__": arg_count,
                "__expected_posargs__": pos_count,
                "__expected_kwargs__": kw_count,
            },
        )

class PARTIAL(FUNC):
    def __term__(typ, trm):
        return super().__term__(trm) and getattr(trm, 'is_partial', False)

class DOM_FUNC(FUNC):
    def __term__(typ, trm):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import Function

        if not super().__term__(trm):
            return False

        if not term(trm, Function):
            return False

        dom_value = None
        if hasattr(trm, "dom"):
            dom_value = getattr(trm, "dom")
        elif hasattr(trm, "domain"):
            dom_value = getattr(trm, "domain")
        else:
            return False

        expected_dom = getattr(typ, "__types__", None)
        if expected_dom is not None:
            try:
                actual = tuple(dom_value)
            except TypeError:
                actual = (dom_value,)
            return actual == expected_dom

        if not term(dom_value, tuple):
            return False
        return all(term(t, TYPE) for t in dom_value)

    def __call__(typ, *types, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import DomFunc as DomFunc
        from typed.mods.helper.helper import _name_list

        if not types and not kwargs:
            return typ

        if types and all(term(t, TYPE) for t in types) and not kwargs:
            class_name = f"DomFunc({_name_list(*types)})"
            return DOM_FUNC(
                class_name,
                (DomFunc,),
                {
                    "__display__": class_name,
                    "__types__": tuple(types),
                },
            )

        raise TypeError("DomFunc(X, Y, ...) expects TYPE arguments only")

class COD_FUNC(FUNC):
    def __term__(typ, trm):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import Function

        if not super().__term__(trm):
            return False

        if not term(trm, Function):
            return False

        cod_value = None
        if hasattr(trm, "cod"):
            cod_value = getattr(trm, "cod")
        elif hasattr(trm, "codomain"):
            cod_value = getattr(trm, "codomain")
        else:
            return False

        expected = getattr(typ, "__codomain__", None)
        if expected is not None:
            return cod_value is expected

        return term(cod_value, TYPE)

    def __call__(typ, cod=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import CodFunc
        from typed.mods.helper.helper import _name

        if cod is None and not kwargs:
            return typ

        if term(cod, TYPE) and not kwargs:
            class_name = f"CodFunc({_name(cod)})"
            return COD_FUNC(
                class_name,
                (CodFunc,),
                {
                    "__display__": class_name,
                    "__codomain__": cod,
                },
            )

        raise TypeError("CodFunc(X) expects a single TYPE argument")


class COMP_FUNC(DOM_FUNC, COD_FUNC):
    def __term__(typ, trm):
        from typed.mods.types.func import DomFunc, CodFunc

        if not term(trm, DomFunc):
            return False
        if not term(trm, CodFunc):
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

    def __call__(typ, *types, cod=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import CompFunc
        from typed.mods.helper.helper import _name_list, _name

        if not types and cod is None and not kwargs:
            return typ

        if (
            types
            and all(term(t, TYPE) for t in types)
            and term(cod, TYPE)
            and not kwargs
        ):
            class_name = f"CompFunc({_name_list(*types)}, cod={_name(cod)})"
            return COMP_FUNC(
                class_name,
                (CompFunc,),
                {
                    "__display__": class_name,
                    "__types__": tuple(types),
                    "__codomain__": cod,
                },
            )

        raise TypeError("CompFunc(X, Y, ..., cod=Z) expects TYPE arguments only")


class DOM_HINTED(DOM_FUNC, PARTIAL):
    """
    Metatype for DomHinted.

    Cases:
      1) DOM_HINTED(f) where f in DomFunc  -> DomHinted(f)
      2) DOM_HINTED(T1, T2, ...) (Ti in TYPE) -> parametric DomHinted(T1,T2,...)
    """
    def __term__(typ, trm):
        if issubclass(type(trm), typ):
            return True
        if not super().__term__(trm):
            return False
        from typed.mods.helper.func import _is_domain_hinted
        try:
            return _is_domain_hinted(trm.func)
        except Exception:
            return False

    def __call__(typ, *args, **kwargs):
        from typed.mods.types.base  import TYPE
        from typed.mods.types.func  import DomFunc as DomFuncType, DomHinted as DomHintedType
        from typed.mods.helper.general import _name_list

        if not args and not kwargs:
            return typ

        # 1) DOM_HINTED(f) where f is DomFunc -> DomHinted(f)
        if len(args) == 1 and term(args[0], DomFuncType) and not kwargs:
            f = args[0]
            return type.__call__(DomHintedType, f)

        # 2) DOM_HINTED(T1, T2, ...)  all Ti in TYPE -> a DomHinted parametric type
        if args and all(term(t, TYPE) for t in args) and not kwargs:
            types = tuple(args)
            class_name = f"DomHinted({_name_list(*types)})"

            # behavior from old _DomHinted_
            class PARAM(typ):
                __display__ = class_name
                __types__   = types

                def __term__(self, trm):
                    if not term(trm, DomHintedType):
                        return False
                    domain_hints = set(_hinted_domain(trm.func))
                    return domain_hints == set(self.__types__)

                def check(self, trm):
                    if not callable(trm):
                        return False
                    domain_hints = set(_hinted_domain(trm))
                    return domain_hints == set(self.__types__)

            return PARAM(class_name, (DomHintedType,), {"__display__": class_name, "__types__": types})

        raise TypeError(
            f"{typ.__name__}(): expected 0 args, or a DomFunc, or TYPE arguments"
        )


class COD_HINTED(COD_FUNC, PARTIAL):
    """
    Metatype for CodHinted.

    Cases:
      1) COD_HINTED(f) where f in CodFunc -> CodHinted(f)
      2) COD_HINTED(R) where R in TYPE   -> parametric CodHinted(R)
    """
    def __term__(typ, trm):
        from typed.mods.types.base import TYPE
        from typed.mods.helper.func import _is_codomain_hinted

        if _issubtype(TYPE(trm), typ):
            return True
        if not super().__term__(trm):
            return False
        try:
            return _is_codomain_hinted(trm.func)
        except Exception:
            return False

    def __call__(typ, *args, **kwargs):
        from typed.mods.types.base  import TYPE
        from typed.mods.types.func  import CodFunc as CodFuncType, CodHinted as CodHintedType
        from typed.mods.helper.general import _name

        if not args and not kwargs:
            return typ

        # 1) COD_HINTED(f) where f is CodFunc -> CodHinted(f)
        if len(args) == 1 and term(args[0], CodFuncType) and not kwargs:
            f = args[0]
            return type.__call__(CodHintedType, f)

        # 2) COD_HINTED(R) where R in TYPE -> parametric CodHinted(R)
        if len(args) == 1 and term(args[0], TYPE) and not kwargs:
            cod = args[0]
            class_name = f"CodHinted(cod={_name(cod)})"

            class PARAM(typ):
                __display__  = class_name
                __codomain__ = cod

                def __term__(self, trm):
                    if not term(trm, CodHintedType):
                        return False
                    return_hint = _hinted_codomain(trm.func)
                    return return_hint == self.__codomain__

                def check(self, trm):
                    if not callable(trm):
                        return False
                    return_hint = _hinted_codomain(trm)
                    return return_hint == self.__codomain__

            return PARAM(class_name, (CodHintedType,), {"__display__": class_name, "__codomain__": cod})

        raise TypeError(
            f"{typ.__name__}(): expected 0 args, or a CodFunc, or a single TYPE"
        )


class HINTED(COMP_FUNC, COD_HINTED, DOM_HINTED):
    """
    Metatype for Hinted.

    Cases:
      1) HINTED(f) where f is callable/dom+cod hinted -> Hinted(f)
      2) HINTED(T1, ..., cod=R)  -> parametric Hinted(T1,...; cod=R)
    """
    def __term__(typ, trm):
        return super().__term__(trm)

    def __call__(typ, *args, **kwargs):
        from typed.mods.types.base  import TYPE
        from typed.mods.types.func  import Hinted as HintedType
        from typed.mods.helper.general import _name_list, _name

        if not args and not kwargs:
            return typ

        # 1) HINTED(f) where f is already Hinted or callable compatible
        if len(args) == 1 and term(args[0], HintedType) and not kwargs:
            return args[0]

        if len(args) == 1 and callable(args[0]) and not kwargs:
            f = args[0]
            # Let the Hinted class do its own init (it checks hints)
            return type.__call__(HintedType, f)

        # 2) HINTED(T1,...,Tk, cod=R)  with Ti,R in TYPE -> parametric type
        if "cod" in kwargs and all(term(t, TYPE) for t in args):
            cod = kwargs["cod"]
            if not term(cod, TYPE):
                raise TypeError(
                    f"Hinted(..., cod=R): R must be TYPE, got '{_name(type(cod))}'"
                )
            types = tuple(args)
            class_name = f"Hinted({_name_list(*types)}; {_name(cod)})"

            class PARAM(typ):
                __display__  = class_name
                __types__    = types
                __codomain__ = cod

                def __term__(self, trm):
                    if not term(trm, HintedType):
                        return False
                    domain_hints = set(_hinted_domain(trm.func))
                    return_hint  = _hinted_codomain(trm.func)
                    return (domain_hints == set(self.__types__)
                            and return_hint  == self.__codomain__)

                def check(self, trm):
                    if not callable(trm):
                        return False
                    domain_hints = set(_hinted_domain(trm))
                    return_hint  = _hinted_codomain(trm)
                    return (domain_hints == set(self.__types__)
                            and return_hint  == self.__codomain__)

            return PARAM(
                class_name,
                (HintedType,),
                {
                    "__display__":  class_name,
                    "__types__":    types,
                    "__codomain__": cod,
                },
            )

        raise TypeError(
            f"{typ.__name__}(): expected 0 args, or a Hinted‑compatible function, "
            "or TYPE arguments plus cod=TYPE"
        )


class DOM_TYPED(DOM_HINTED):
    """
    Metatype for DomTyped.

    Cases:
      1) DOM_TYPED(f) where f in DomFunc  -> DomTyped(f)
      2) DOM_TYPED(T1, ..., Tk) (Ti in TYPE) -> parametric DomTyped(T1,...,Tk)
    """
    def __term__(typ, trm):
        return super().__term__(trm)

    def __call__(typ, *args, **kwargs):
        from typed.mods.types.base  import TYPE
        from typed.mods.types.func  import DomFunc as DomFuncType, DomTyped as DomTypedType
        from typed.mods.helper.general import _name_list

        if not args and not kwargs:
            return typ

        # 1) DomFunc trm -> DomTyped trm
        if len(args) == 1 and term(args[0], DomFuncType) and not kwargs:
            f = args[0]
            return type.__call__(DomTypedType, f)

        # 2) DOM_TYPED(T1, ..., Tk)
        if args and all(term(t, TYPE) for t in args) and not kwargs:
            types = tuple(args)
            class_name = f"DomTyped({_name_list(*types)})"

            class PARAM(typ):
                __display__ = class_name
                __types__   = types

                def __term__(self, trm):
                    if not term(trm, DomTypedType):
                        return False
                    domain_hints = set(_hinted_domain(trm.func))
                    return domain_hints == set(self.__types__)

                def check(self, trm):
                    if not callable(trm):
                        return False
                    domain_hints = set(_hinted_domain(trm))
                    return domain_hints == set(self.__types__)

            return PARAM(class_name, (DomTypedType,), {"__display__": class_name, "__types__": types})

        raise TypeError(
            f"{typ.__name__}(): expected 0 args, or a DomFunc, or TYPE arguments"
        )


class COD_TYPED(COD_HINTED):
    """
    Metatype for CodTyped.

    Cases:
      1) COD_TYPED(f) where f in CodFunc -> CodTyped(f)
      2) COD_TYPED(R) where R in TYPE    -> parametric CodTyped(R)
    """
    def __term__(typ, trm):
        return super().__term__(trm)

    def __call__(typ, *args, **kwargs):
        from typed.mods.types.base  import TYPE
        from typed.mods.types.func  import CodFunc as CodFuncType, CodTyped as CodTypedType
        from typed.mods.helper.general import _name

        if not args and not kwargs:
            return typ

        # 1) CodFunc trm -> CodTyped trm
        if len(args) == 1 and term(args[0], CodFuncType) and not kwargs:
            f = args[0]
            return type.__call__(CodTypedType, f)

        # 2) Single TYPE codomain
        if len(args) == 1 and term(args[0], TYPE) and not kwargs:
            cod = args[0]
            class_name = f"CodTyped(cod={_name(cod)})"

            class PARAM(typ):
                __display__  = class_name
                __codomain__ = cod

                def __term__(self, trm):
                    if not term(trm, CodTypedType):
                        return False
                    return_hint = _hinted_codomain(trm.func)
                    return return_hint == self.__codomain__

                def check(self, trm):
                    if not callable(trm):
                        return False
                    return_hint = _hinted_codomain(trm)
                    return return_hint == self.__codomain__

            return PARAM(class_name, (CodTypedType,), {"__display__": class_name, "__codomain__": cod})

        raise TypeError(
            f"{typ.__name__}(): expected 0 args, or a CodFunc, or a single TYPE"
        )


class TYPED(HINTED, DOM_TYPED, COD_TYPED):
    """
    Metatype for Typed.

    Cases:
      1) TYPED(f) where f is a plain function -> Typed(f)
      2) TYPED(T1,..., Tk, cod=R) -> parametric Typed(T1,...,Tk; cod=R)
    """
    def __term__(typ, trm):
        if getattr(trm, 'is_partial', False):
            orig = getattr(trm, 'original_func', None)
            if orig is None:
                return False

            if getattr(orig, 'is_lazy', False):
                return False

            return term(orig, typ)

        if getattr(trm, "is_lazy", False):
            return False

        return super().__term__(trm)

    def check(self, trm):
        if hasattr(self, "__types__"):
            domain_hints = set(_hinted_domain(trm))
            return_hint  = _hinted_codomain(trm)
            return domain_hints == set(self.__types__) and return_hint == self.__codomain__
        return True

    def __call__(typ, *args, **kwargs):
        from typed.mods.types.func import Typed as TypedType
        from typed.mods.types.base import TYPE
        from typed.mods.helper.general import _name_list, _name

        # Typed(f) for raw function -> trm
        if typ is TypedType or issubclass(typ, TypedType):
            if len(args) == 1 and inspect.isfunction(args[0]) and not term(args[0], TypedType) and not kwargs:
                return type.__call__(TypedType, args[0])

        if not args and not kwargs:
            return typ

        # Case #1: single callable -> Typed trm
        if len(args) == 1 and callable(args[0]) and not kwargs:
            f = args[0]
            return type.__call__(TypedType, f)

        # Case #2: parametric Typed(T1,...,Tk, cod=R)
        if "cod" in kwargs and all(term(t, TYPE) for t in args):
            cod = kwargs["cod"]
            if not term(cod, TYPE):
                raise TypeError(
                    f"Typed(..., cod=R): R must be TYPE, got '{_name(type(cod))}'"
                )
            types = tuple(args)
            class_name = f"Typed({_name_list(*types)}, cod={_name(cod)})"

            class PARAM(typ):
                __display__  = class_name
                __types__    = types
                __codomain__ = cod

                def __term__(self, trm):
                    if not term(trm, TypedType):
                        return False
                    domain_hints = set(_hinted_domain(trm.func))
                    return_hint  = _hinted_codomain(trm.func)
                    from typed.mods.types.base import Any
                    if len(self.__types__) == 1 and self.__types__[0] is Any:
                        return return_hint == self.__codomain__
                    return (domain_hints == set(self.__types__)
                            and return_hint  == self.__codomain__)

                def check(self, trm):
                    if not callable(trm):
                        return False
                    domain_hints = set(_hinted_domain(trm))
                    return_hint  = _hinted_codomain(trm)
                    return (domain_hints == set(self.__types__)
                            and return_hint  == self.__codomain__)

            return PARAM(
                class_name,
                (TypedType,),
                {
                    "__display__":  class_name,
                    "__types__":    types,
                    "__codomain__": cod,
                },
            )

        raise TypeError(
            f"{typ.__name__}(): expected 0 args, or a callable, or TYPE arguments plus cod=TYPE"
        )


class CONDITION(TYPED):
    def __term__(typ, trm):
        from typed.mods.types.base import Bool
        return super().__term__(trm) and trm.cod is Bool

    def __call__(typ, *args, **kwargs):
        from typed.mods.types.func import Condition as ConditionType, Typed as TypedType
        from typed.mods.types.base import TYPE, Bool
        from typed.mods.helper.general import _name, _name_list

        if typ is ConditionType or issubclass(typ, ConditionType):
            if len(args) == 1 and inspect.isfunction(args[0]) and not term(args[0], ConditionType) and not kwargs:
                typed = TypedType(args[0])
                if typed.cod is not Bool:
                    raise TypeError(
                        f"Wrong type in codomain of '{_name(args[0])}':\n"
                        f" ==> '{_name(typed.cod)}' is not 'Bool'"
                    )
                return type.__call__(ConditionType, args[0])

        if not args and not kwargs:
            return typ

        if len(args) == 1 and callable(args[0]) and not kwargs:
            typed = TypedType(args[0])
            if typed.cod is not Bool:
                raise TypeError(
                    f"Wrong type in codomain of '{_name(args[0])}':\n"
                    f" ==> '{_name(typed.cod)}' is not 'Bool'"
                )
            return type.__call__(ConditionType, args[0])

        if args and all(term(t, TYPE) for t in args) and not kwargs:
            types = tuple(args)
            class_name = f"Condition({_name_list(*types)})"

            class PARAM(typ):
                __display__  = class_name
                __types__    = types
                __codomain__ = Bool

                def __term__(self, trm):
                    if not term(trm, ConditionType):
                        return False
                    domain_hints = set(_hinted_domain(trm.func))
                    return_hint  = _hinted_codomain(trm.func)
                    return (domain_hints == set(self.__types__)
                            and return_hint  == self.__codomain__)

                def check(self, trm):
                    if not callable(trm):
                        return False
                    domain_hints = set(_hinted_domain(trm))
                    return_hint  = _hinted_codomain(trm)
                    return (domain_hints == set(self.__types__)
                            and return_hint  == self.__codomain__)

            return PARAM(
                class_name,
                (ConditionType,),
                {
                    "__display__":  class_name,
                    "__types__":    types,
                    "__codomain__": Bool,
                },
            )

        raise TypeError(
            f"{typ.__name__}(): expected 0 args, or a Bool‑returning callable, or TYPE arguments"
        )


class FACTORY(TYPED):
    def __term__(typ, trm):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import Typed
        if trm == Typed.__call__:
            return True
        return term(trm, Typed) and _issubtype(trm.cod, TYPE)

class OPERATION(FACTORY):
    def __term__(typ, trm):
        from typed.mods.types.base import TYPE, Tuple
        return super().__term__(trm) and _issubtype(trm.dom, Tuple(TYPE))

class DEPENDENT(FACTORY):
    def __term__(typ, trm):
        if super().__term__(trm) and hasattr(trm, "is_dependent_type"):
            return trm.is_dependent_type
        return False

class LAZY(HINTED):
    def __term__(typ, trm):
        if getattr(trm, "is_partial", False):
            orig = getattr(trm, "original_func", None)
            if orig is not None:
                return term(orig, typ)
            return False

        if getattr(trm, "is_lazy", False):
            return True

        return False

    def __call__(typ, *args, **kwargs):
        import inspect
        from typed.mods.types.func import Lazy

        if (typ is Lazy or issubclass(typ, Lazy)) \
           and len(args) == 1 \
           and inspect.isfunction(args[0]) \
           and not term(args[0], Lazy):
            return type.__call__(Lazy, args[0])

        return super().__call__(*args, **kwargs)

