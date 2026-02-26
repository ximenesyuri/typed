import inspect
from typed.mods.meta.base import _TYPE_
from typed.mods.helper.general import _name, _issubtype
from typed.mods.helper.func import (
    _unwrap,
    _get_num_args,
    _get_num_posargs,
    _get_num_kwargs
)

class CALLABLE(_TYPE_):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE
        if _issubtype(TYPE(instance), cls):
            return True
        unwrapped = instance
        while hasattr(unwrapped, 'func') and unwrapped.func is not unwrapped:
            unwrapped = unwrapped.func

        return (
            inspect.isbuiltin(unwrapped)
            or inspect.ismethod(unwrapped)
            or inspect.isfunction(unwrapped)
            or inspect.isclass(unwrapped)
        )

class GENERATOR(_TYPE_):
    def __instancecheck__(cls, instance):
        return (
            inspect.isgeneratorfunction(instance)
            or inspect.isasyncgenfunction(instance)
        )

class BUILTIN(CALLABLE):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            from typed.mods.types.base import TYPE
            if _issubtype(TYPE(instance), cls):
                return True
            unwrapped = instance.func if hasattr(instance, 'func') else instance
            return inspect.isbuiltin(unwrapped)
        return False

class CLASS(CALLABLE):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            from typed.mods.types.base import TYPE
            if _issubtype(TYPE(instance), cls):
                return True
            return inspect.isclass(instance)
        return False

class BOUND_METHOD(CALLABLE):
    def __instancecheck__(cls, instance):
        return inspect.ismethod(instance) and instance.__self__ is not None

class UNBOUND_METHOD(CALLABLE):
    def __instancecheck__(cls, instance):
        return inspect.isfunction(instance) and '.' in getattr(instance, '__qualname__', '')

class METHOD(CALLABLE):
    def __instancecheck__(cls, instance):
        return (
            inspect.ismethod(instance) and instance.__self__ is not None
            or inspect.isfunction(instance) and '.' in getattr(instance, '__qualname__', '')
        )

class LAMBDA(CALLABLE):
    def __instancecheck__(cls, instance):
        return (
            inspect.isfunction(instance)
            and instance.__name__ == '<lambda>'
            and not inspect.ismethod(instance)
            and not inspect.isbuiltin(instance)
        )

class FUNCTION(CALLABLE):
    def __instancecheck__(cls, instance):
        if not super().__instancecheck__(instance):
            return False

        from typed.mods.types.base import TYPE

        if _issubtype(TYPE(instance), cls):
            base_ok = True
        else:
            unwrapped = instance.func if hasattr(instance, "func") else instance
            base_ok = (
                inspect.isfunction(unwrapped)
                and unwrapped.__name__ != "<lambda>"
                and not inspect.ismethod(unwrapped)
                and not inspect.isbuiltin(unwrapped)
            )

        if not base_ok:
            return False

        expected_args = getattr(cls, "__expected_args__", -1)
        expected_pos = getattr(cls, "__expected_posargs__", -1)
        expected_kw = getattr(cls, "__expected_kwargs__", -1)

        if expected_args < 0 and expected_pos < 0 and expected_kw < 0:
            return True

        target = _unwrap(instance)

        if expected_args >= 0 and _get_num_args(target) != expected_args:
            return False
        if expected_pos >= 0 and _get_num_posargs(target) != expected_pos:
            return False
        if expected_kw >= 0 and _get_num_kwargs(target) != expected_kw:
            return False

        return True

    def __call__(cls, *call_args, **call_kwargs):
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
            if not isinstance(value, int):
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

            return f

        if arg_count < 0 and pos_count < 0 and kw_count < 0:
            return cls

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

        return FUNCTION(
            class_name,
            (Function,),
            {
                "__display__": class_name,
                "__expected_args__": arg_count,
                "__expected_posargs__": pos_count,
                "__expected_kwargs__": kw_count,
            },
        )

class PARTIAL(FUNCTION):
    def __instancecheck__(cls, instance):
        return super().__instancecheck__(instance) and getattr(instance, 'is_partial', False)

class ATTR_FUNC(FUNCTION):
    def __instancecheck__(cls, instance):
        if not super().__instancecheck__(instance):
            return False

        attrs = getattr(cls, "__attrs__", ())
        attr_values = getattr(cls, "__attr_values__", {})

        for name in attrs:
            if not hasattr(instance, name):
                return False

        for name, expected in attr_values.items():
            if not hasattr(instance, name):
                return False
            if getattr(instance, name) != expected:
                return False

        return True

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.func import AttrFunc as AttrFunc
        from typed.mods.helper.helper import _name

        if not args and not kwargs:
            return cls

        attrs = tuple(a.lstrip('.') for a in args)
        attr_values = {k.lstrip('.'): v for k, v in kwargs.items()}

        parts = []
        if attrs:
            parts.append(", ".join(attrs))
        if attr_values:
            vals_str = ", ".join(f"{k}={_name(v)}" for k, v in attr_values.items())
            parts.append(vals_str)
        inside = "; ".join(parts)

        class_name = f"AttrFunc({inside})"

        return ATTR_FUNC(
            class_name,
            (AttrFunc,),
            {
                "__display__": class_name,
                "__attrs__": attrs,
                "__attr_values__": attr_values,
            },
        )


class DOM_FUNC(FUNCTION):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import Function

        if not super().__instancecheck__(instance):
            return False

        if not isinstance(instance, Function):
            return False

        dom_value = None
        if hasattr(instance, "dom"):
            dom_value = getattr(instance, "dom")
        elif hasattr(instance, "domain"):
            dom_value = getattr(instance, "domain")
        else:
            return False

        expected_dom = getattr(cls, "__types__", None)
        if expected_dom is not None:
            try:
                actual = tuple(dom_value)
            except TypeError:
                actual = (dom_value,)
            return actual == expected_dom

        if not isinstance(dom_value, tuple):
            return False
        return all(isinstance(t, TYPE) for t in dom_value)

    def __call__(cls, *types, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import DomFunc as DomFunc
        from typed.mods.helper.helper import _name_list

        if not types and not kwargs:
            return cls

        if types and all(isinstance(t, TYPE) for t in types) and not kwargs:
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

class COD_FUNC(FUNCTION):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import Function

        if not super().__instancecheck__(instance):
            return False

        if not isinstance(instance, Function):
            return False

        cod_value = None
        if hasattr(instance, "cod"):
            cod_value = getattr(instance, "cod")
        elif hasattr(instance, "codomain"):
            cod_value = getattr(instance, "codomain")
        else:
            return False

        expected = getattr(cls, "__codomain__", None)
        if expected is not None:
            return cod_value is expected

        return isinstance(cod_value, TYPE)

    def __call__(cls, cod=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import CodFunc
        from typed.mods.helper.helper import _name

        if cod is None and not kwargs:
            return cls

        if isinstance(cod, TYPE) and not kwargs:
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
    def __instancecheck__(cls, instance):
        from typed.mods.types.func import DomFunc, CodFunc

        if not isinstance(instance, DomFunc):
            return False
        if not isinstance(instance, CodFunc):
            return False

        dom_types = getattr(cls, "__types__", None)
        cod_type = getattr(cls, "__codomain__", None)

        if dom_types is not None:
            dom = getattr(instance, "dom", getattr(instance, "domain", None))
            try:
                actual_dom = tuple(dom)
            except TypeError:
                actual_dom = (dom,)
            if actual_dom != dom_types:
                return False

        if cod_type is not None:
            cod = getattr(instance, "cod", getattr(instance, "codomain", None))
            if cod is not cod_type:
                return False

        return True

    def __call__(cls, *types, cod=None, **kwargs):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import CompFunc
        from typed.mods.helper.helper import _name_list, _name

        if not types and cod is None and not kwargs:
            return cls

        if (
            types
            and all(isinstance(t, TYPE) for t in types)
            and isinstance(cod, TYPE)
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
    Build the 'hinted-domain function type' of types:
        > the objects of 'HintedDom(X, Y, ...)'
        > are objects 'f(x: X, y: Y, ...)' of 'HintedDom'
    The case 'HintedDom(n, m)' is the restriction of
    'Function(n, m)' to 'HintedDom'
    """
    def __instancecheck__(cls, instance):
        if issubclass(type(instance), cls):
            return True
        if not super().__instancecheck__(instance):
            return False
        from typed.mods.helper.helper import _is_domain_hinted
        try:
            return _is_domain_hinted(instance.func)
        except:
            return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.base  import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int):
            from typed.mods.parametric.func  import _HintedDom_
            return _HintedDom_(args[0])
        if args and all(isinstance(t, TYPE) for t in args) and not kwargs:
            from typed.mods.parametric.func  import _HintedDom_
            return _HintedDom_(*args, **kwargs)
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types")

class COD_HINTED(COD_FUNC, PARTIAL):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE
        if _issubtype(TYPE(instance), cls):
            return True
        if not super().__instancecheck__(instance):
            return False
        from typed.mods.helper.helper import _is_codomain_hinted
        try:
            return _is_codomain_hinted(instance.func)
        except:
            return False

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.base  import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int):
            from typed.mods.parametric.func  import _HintedCod_
            return _HintedCod_(args[0])
        if len(args)==1 and isinstance(args[0], TYPE):
            from typed.mods.parametric.func  import _HintedCod_
            return _HintedCod_(args[0])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or a single type")

class HINTED(COMP_FUNC, COD_HINTED, DOM_HINTED):
    def __instancecheck__(cls, instance):
        return super().__instancecheck__(instance)

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.base  import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int) and not kwargs:
            from typed.mods.parametric.func  import _Hinted_
            return _Hinted_(args[0])
        if 'cod' in kwargs and all(isinstance(t, TYPE) for t in args):
            from typed.mods.parametric.func  import _Hinted_
            return _Hinted_(*args, cod=kwargs['cod'])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types+cod=Type")

class DOM_TYPED(DOM_HINTED):
    def __instancecheck__(cls, instance):
        return super().__instancecheck__(instance)

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.base  import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int):
            from typed.mods.parametric.func  import _TypedDom_
            return _TypedDom_(args[0])
        if args and all(isinstance(t, TYPE) for t in args) and not kwargs:
            from typed.mods.parametric.func  import _TypedDom_
            return _TypedDom_(*args)
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types")

class COD_TYPED(COD_HINTED):
    def __instancecheck__(cls, instance):
        return super().__instancecheck__(instance)

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.base  import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int):
            from typed.mods.parametric.func  import _TypedCod_
            return _TypedCod_(args[0])
        if len(args)==1 and isinstance(args[0], TYPE):
            from typed.mods.parametric.func  import _TypedCod_
            return _TypedCod_(args[0])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or a single type")

class TYPED(HINTED, DOM_TYPED, COD_TYPED):
    def __instancecheck__(cls, instance):
        if getattr(instance, 'is_partial', False):
            orig = getattr(instance, 'original_func', None)
            if orig is None:
                return False

            if getattr(orig, 'is_lazy', False):
                return False

            return isinstance(orig, cls)

        if getattr(instance, "is_lazy", False):
            return False

        return super().__instancecheck__(instance)

    def check(self, instance):
        if hasattr(self, "__types__"):
            from typed.mods.helper.helper import _hinted_domain, _hinted_codomain
            domain_hints = set(_hinted_domain(instance))
            return_hint = _hinted_codomain(instance)
            return domain_hints == set(self.__types__) and return_hint == self.__codomain__
        return True

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.func import Typed
        if cls is Typed or issubclass(cls, Typed):
            if len(args) == 1 and inspect.isfunction(args[0]) and not isinstance(args[0], Typed):
                return type.__call__(Typed, args[0])
        from typed.mods.types.base import TYPE, Int
        if not args and not kwargs:
            return cls
        if len(args)==1 and callable(args[0]) and not kwargs:
            return super().__call__(*args)
        if len(args)==1 and isinstance(args[0], Int) and not kwargs:
            from typed.mods.parametric.func  import _Typed_
            return _Typed_(args[0])
        if 'cod' in kwargs and all(isinstance(t, TYPE) for t in args):
            from typed.mods.parametric.func  import _Typed_
            return _Typed_(*args, cod=kwargs['cod'])
        raise TypeError(f"{cls.__name__}(): expected 0 args, or a callable, or int>0, or types+cod=Type")

class CONDITION(TYPED):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import Bool
        return super().__instancecheck__(instance) and instance.cod is Bool

    def __call__(cls, *args, **kwargs):
        from typed.mods.types.func import Condition
        if cls is Condition or issubclass(cls, Condition):
            if len(args) == 1 and inspect.isfunction(args[0]) and not isinstance(args[0], Condition):
                from typed.mods.types.base import Bool
                typed = super().__call__(args[0])
                if typed.cod is not Bool:
                    from typed.mods.types.base import TYPE
                    raise TypeError(
                        f"Wrong type in codomain of '{_name(args[0])}':\n"
                        f" ==> '{_name(typed.cod)}' is not 'Bool'"
                    )
                return type.__call__(Condition, args[0])
        from typed.mods.types.base import TYPE
        if all(isinstance(t, TYPE) for t in args):
            from typed.mods.parametric.func  import _Condition_
            return _Condition_(*args)

class FACTORY(TYPED):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE
        from typed.mods.types.func import Typed
        if instance == Typed.__call__:
            return True
        return isinstance(instance, Typed) and _issubtype(instance.cod, TYPE)

class OPERATION(FACTORY):
    def __instancecheck__(cls, instance):
        from typed.mods.types.base import TYPE, Tuple
        return super().__instancecheck__(instance) and _issubtype(instance.dom, Tuple(TYPE))

class DEPENDENT(FACTORY):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance) and hasattr(instance, "is_dependent_type"):
            return instance.is_dependent_type
        return False

class LAZY(HINTED):
    def __instancecheck__(cls, instance):
        if getattr(instance, "is_partial", False):
            orig = getattr(instance, "original_func", None)
            if orig is not None:
                return isinstance(orig, cls)
            return False

        if getattr(instance, "is_lazy", False):
            return True

        return False

    def __call__(cls, *args, **kwargs):
        import inspect
        from typed.mods.types.func import Lazy

        if (cls is Lazy or issubclass(cls, Lazy)) \
           and len(args) == 1 \
           and inspect.isfunction(args[0]) \
           and not isinstance(args[0], Lazy):
            return type.__call__(Lazy, args[0])

        return super().__call__(*args, **kwargs)

