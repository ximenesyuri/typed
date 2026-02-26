import re
from functools import lru_cache as cache
from typed.mods.helper.null import _null, _null_from_list
from typed.mods.helper.general import (
    _name,
    _name_list,
)

@cache
def Free(Discourse):
    from typed.mods.types.base import TYPE, DISCOURSE
    if not isinstance(Discourse, DISCOURSE):
        raise TypeError(
            "Wrong type in Free factory: \n"
            f" ==> {_name(Discourse)}: has unexpected type\n"
             "     [expected_type] DISCOURSE\n"
            f"     [received_type] {_name(TYPE(Discourse))}"
        )

    from typed.mods.meta.base import _TYPE_
    class FREE(_TYPE_):
        def __instancecheck__(cls, instance):
            return any(instance is x for x in Discourse)
        def __iter__(cls):
            return Discourse.__iter__(cls)

    class_name = f"Free({_name(Discourse)})"
    return FREE(class_name, (), {"__display__": class_name})

@cache
def Inter(*types):
    """
    Build the 'intersection' of types:
        > an object 'p' of the Inter(X, Y, ...)
        > is an object of every 'X, Y, ...'
    """
    from typed.mods.types.base import TYPE
    for t in types:
        if not isinstance(t, TYPE):
            raise TypeError(
                "Wrong type in Union factory: \n"
                f" ==> {_name(t)}: has unexpected type\n"
                 "     [expected_type] TYPE\n"
                f"     [received_type] {_name(TYPE(t))}"
            )
    if types:
        def _key(t):
            return (t.__module__, getattr(t, '__qualname__', t.__name__))
        unique = set(types)
        sorted_types = tuple(sorted(unique, key=_key))
        if len(sorted_types) == 1:
            return sorted_types[0]
        if sorted_types != types:
            return Inter(*sorted_types)
        unique_types = sorted_types
    else:
        unique_types = ()

    non_builtin_types = [t for t in unique_types if not t.__module__ == 'builtins']

    types_ = (TYPE(typ) for typ in unique_types)
    class INTER(*types_):
        def __instancecheck__(cls, instance):
            return all(isinstance(instance, t) for t in non_builtin_types)
        def __subclasscheck__(cls, subclass):
            return all(issubclass(subclass, t) for t in unique_types)

    __null__ = list(set(_null(t) for t in types))

    class_name = f"Inter({_name_list(*unique_types)})"
    try:
        return INTER(class_name, unique_types, {
            '__display__': class_name,
            '__types__': unique_types,
            '__null__': __null__[0] if len(__null__) == 1 else None
        })
    except Exception:
        return INTER(class_name, (), {
            '__display__': class_name,
            '__types__': unique_types,
            '__null__': __null__[0] if len(__null__) == 1 else None
        })

@cache
def Filter(X, *conds):
    """
    Build the 'filtered type' of a given type through given conditions.
    > An object x is in Filter(X, *conds) iff:
        1. 'x in X' is True
        2. 'cond(x) is True' for 'cond' in 'conds'
    > Each condition can be:
        - a 'Condition' instance
        - a callable that, when wrapped with @typed, returns 'Bool'
    """
    from typed.mods.types.base import TYPE
    from typed.mods.types.func import Condition
    from typed.mods.meta.func import CONDITION

    if not isinstance(X, TYPE):
        raise TypeError(
            "Wrong type in Filter factory: \n"
            f" ==> '{_name(X)}': has unexpected type\n"
            "     [expected_type] TYPE\n"
            f"     [received_type] '{_name(TYPE(X))}'"
        )

    if not conds:
        raise TypeError(
            "Wrong usage of Filter factory: \n"
            " ==> no conditions provided\n"
            "     [expected] at least one condition"
        )

    normalized_conditions = []

    for f in conds:
        if getattr(f, "is_lazy", False) and hasattr(f, "materialize"):
            f = f.materialize()

        if isinstance(f, Condition) or TYPE(f) is CONDITION:
            normalized_conditions.append(f)
            continue

        if callable(f):
            from typed.mods.decorators import typed as _typed
            f_typed = _typed(f, lazy=False)

            if isinstance(f_typed, Condition) or TYPE(f_typed) is CONDITION:
                normalized_conditions.append(f_typed)
                continue

        raise TypeError(
            "Wrong type in Filter factory: \n"
            f" ==> '{_name(f)}': has unexpected type\n"
            "     [expected_type] Condition\n"
            f"     [received_type] '{_name(TYPE(f))}'"
        )

    class FILTER(TYPE(X)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, X):
                return False
            return all(cond(instance) for cond in cls.__conditions__)

    from typed.mods.helper.null import _null
    from typed.mods.helper.helper import _name_list

    class_name = f"Filter({_name(X)}; {_name_list(*normalized_conditions)})"
    Filter_ = FILTER(class_name, (X,), {
        "__display__": class_name,
        "__conditions__": tuple(normalized_conditions),
    })

    try:
        Filter_.__null__ = _null(X) if isinstance(_null(X), Filter_) else None
    except Exception:
        Filter_.__null__ = None

    return Filter_


@cache
def Compl(X, *subtypes):
    """
    Build the 'complement subtype' of a type by given subtypes.
    > 'x in Compl(X, *subtypes)' is True iff
        1. 'x in X' is True
        2. 'x in Y' is False for Y in subtypes
    """
    from typed.mods.types.base import TYPE
    if not isinstance(X, TYPE):
        raise TypeError(
            "Wrong type in Compl factory: \n"
            f" ==> '{_name(X)}': has unexpected type\n"
             "     [expected_type] TYPE\n"
            f"     [received_type] {_name(TYPE(X))}"
        )
    unique_subtypes = tuple(set(subtypes))

    for subtype in unique_subtypes:
        if not isinstance(subtype, TYPE):
            raise TypeError(
                "Wrong type in Compl factory: \n"
                f" ==> {_name(subtype)}: has unexpected type\n"
                 "     [expected_type] Typed\n"
                f"     [received_type] {_name(TYPE(subtype))}"
            )
        if not issubclass(subtype, X):
            raise TypeError(
                "Wrong type in Compl factory: \n"
                f" ==> {_name(subtype)}: has unexpected type\n"
                f"     [expected_type] a subtype of {_name(X)}\n"
                f"     [received_type] {_name(TYPE(subtype))}"
            )

    class_name = f"Compl({_name(X)}; {_name_list(*subtypes)})"

    class COMPL(TYPE(X)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, cls.__base_type__):
                return False
            return not any(isinstance(instance, subtype) for subtype in cls.__excluded_subtypes__)

    Compl_ = COMPL(class_name, (X,), {
        "__display__": class_name,
        '__base_type__': X,
        '__excluded_subtypes__': unique_subtypes
    })
    Compl_.__null__ = _null(X) if isinstance(_null(X), Compl_) else None
    return Compl_

@cache
def Regex(regex):
    """
    Build the 'regex type' for a given regex:
    > 'x in Regex(r'regex')' is True iff:
        1. 'x in Str' is True
        2. 're.compile(regex).match(x)' is True
    """
    from typed.mods.types.base import Pattern
    if not isinstance(regex, Pattern):
        from typed.mods.types.base import TYPE
        raise TypeError(
            "Wrong type in Regex factory: \n"
            f" ==> {regex}: has unexpected type\n"
             "     [expected_type] Pattern\n"
            f"     [received_type] {_name(TYPE(regex))}"
        )

    from typed.mods.types.base import Str, TYPE
    class REGEX(TYPE(Str)):
        def __new__(cls, name, bases, dct):
            dct['_regex_pattern'] = re.compile(regex)
            dct['_regex'] = regex
            return super().__new__(cls, name, bases, dct)

        def __instancecheck__(cls, instance):
            x = re.compile(regex)
            return isinstance(instance, Str) and x.match(instance) is not None

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, Str)

    class_name = f"Regex({regex})"
    Regex_ = REGEX(class_name, (Str,), {
        "__display__": class_name,
    })
    Regex_.__null__ = "" if isinstance("", Regex_) else None
    return Regex_

@cache
def Interval(typ, start, end, ops=('<=', '<=')):
    """
    Build the 'interval subtype' of given type.
    > 'x in Interval(X, x1, x2, ops=(op1, op2))' is True iff
        1. 'x1 in X' is True
        2. 'x2 in X' is True
        3. 'op1(x1, x)' is True
        4. 'op2(x, x2)' is True
    > op1, op2 could be:
        1. strings '<=, <, >=, >'
        2. strings 'le, lr, ge, gt'
        3. callables from the 'operation' lib
    """

    from typed.mods.types.base import TYPE
    from typed.mods.factories.meta import ATTR

    if not isinstance(typ, TYPE):
        raise TypeError(
            "Wrong type in Interval factory: \n"
            f" ==> '{_name(typ)}': has unexpected type\n"
            "     [expected_type] TYPE\n"
            f"     [received_type] '{_name(TYPE(typ))}'"
        )

    if not isinstance(start, typ):
        raise TypeError(
            "Wrong type in Interval factory: \n"
            f" ==> {start}: has unexpected type\n"
            f"     [expected_type] {_name(typ)}\n"
            f"     [received_type] {_name(TYPE(start))}"
        )
    if not isinstance(end, typ):
        raise TypeError(
            "Wrong type in Interval factory: \n"
            f" ==> {end}: has unexpected type\n"
            f"     [expected_type] {_name(typ)}\n"
            f"     [received_type] {_name(TYPE(end))}"
        )

    from operator import le, lt, ge, gt

    def _normalize_one(op):
        mapping = {
            'le':  ('__le__', le),
            '<=':  ('__le__', le),
            '__le__': ('__le__', le),

            'lt':  ('__lt__', lt),
            '<':   ('__lt__', lt),
            '__lt__': ('__lt__', lt),

            'ge':  ('__ge__', ge),
            '>=':  ('__ge__', ge),
            '__ge__': ('__ge__', ge),

            'gt':  ('__gt__', gt),
            '>':   ('__gt__', gt),
            '__gt__': ('__gt__', gt),
        }

        if isinstance(op, str):
            key = op.strip()
            if key in mapping:
                return mapping[key]

        if callable(op):
            func_to_attr = {
                le: '__le__',
                lt: '__lt__',
                ge: '__ge__',
                gt: '__gt__',
            }
            if op in func_to_attr:
                return func_to_attr[op], op

        raise TypeError(
            "Wrong operation in Interval factory: \n"
            f" ==> {op!r}: has unexpected value/type\n"
            "     [expected] '<', '<=', '>', '>=', 'lt', 'le', 'gt', 'ge', "
            "or the corresponding functions from 'operator'"
        )

    if not (isinstance(ops, tuple) and len(ops) == 2):
        raise TypeError(
            "Wrong value for 'ops' in Interval factory: \n"
            f" ==> {ops!r}: has unexpected value\n"
            "     [expected] tuple of two comparison operators"
        )

    left_attr,  left_func  = _normalize_one(ops[0])
    right_attr, right_func = _normalize_one(ops[1])

    for attr_name in (left_attr, right_attr):
        if not isinstance(typ, ATTR(attr_name)):
            raise TypeError(
                "Wrong type in Interval factory: \n"
                f" ==> '{_name(typ)}': missing comparison '{attr_name}'\n"
                f"     [expected_type] ATTR('{attr_name}')\n"
                f"     [received_type] '{_name(TYPE(typ))}'"
            )

    class INTERVAL(TYPE(typ)):
        def __new__(
            cls,
            name,
            bases,
            dct,
            base_type,
            lower_bound,
            upper_bound,
            left_op,
            right_op,
        ):
            dct['_base_type'] = base_type
            dct['_lower_bound'] = lower_bound
            dct['_upper_bound'] = upper_bound
            dct['_left_op'] = left_op
            dct['_right_op'] = right_op
            return super().__new__(cls, name, bases, dct)

        def __instancecheck__(cls, instance):
            if not isinstance(instance, cls._base_type):
                return False
            return (
                cls._left_op(cls._lower_bound, instance)
                and cls._right_op(instance, cls._upper_bound)
            )

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, cls._base_type)

    null_value = None
    try:
        if (
            isinstance(start, typ)
            and left_func(start, start)
            and right_func(start, end)
        ):
            null_value = start
        else:
            candidate = _null(typ)
            if (
                candidate is not None
                and isinstance(candidate, typ)
                and left_func(start, candidate)
                and right_func(candidate, end)
            ):
                null_value = candidate
    except Exception:
        null_value = None

    class_name = f"Interval({_name(typ)}, {start}, {end})"
    return INTERVAL(
        class_name,
        (typ,),
        {
            "__display__": class_name,
            "__null__": null_value,
        },
        base_type=typ,
        lower_bound=start,
        upper_bound=end,
        left_op=left_func,
        right_op=right_func,
    )

@cache
def Range(x, y, ops=('<=, <=')):
    from typed.mods.types.base import Int
    typ = Interval(Int, x, y, ops=ops)
    typ.__display__ = f'Range({x}, {y}, ops={ops})'
    return typ

@cache
def Not(*types):
    """
    Build the 'not-type':
        > an object x of Not(X, Y, ...)
        > is NOT an instance of any X, Y, ...
    """
    from typed.mods.types.base import Any, Nill
    from typed.mods.meta.base import _TYPE_

    if not types:
        return Any
    if Any in types:
        return Nill

    class NOT(_TYPE_):
        def __instancecheck__(cls, instance):
            return not any(isinstance(instance, typ) for typ in cls.__types__)

        def __subclasscheck__(cls, subclass):
            return not any(issubclass(subclass, typ) for typ in cls.__types__)

    class_name = f"Not({_name_list(*types)})"
    return NOT(class_name, (), {
        "__display__": class_name,
        '__types__': types,
        '__null__': None
    })

@cache
def Null(typ):
    from typed.mods.types.base import TYPE
    if not isinstance(typ, TYPE):
        raise TypeError(
            "Wrong type in 'Null' factory: \n"
            f" ==> '{_name(typ)}': has unexpected type\n"
             "     [expected_type] TYPE"
            f"     [received_type] {_name(TYPE(typ))}"
        )

    from typed.mods.types.base import Nill
    if typ is Nill:
        return Nill

    class NULL(TYPE(typ)):
        def __instancecheck__(cls, instance):
            return instance == _null(typ)
        def __repr__(cls):
            return f"<Null({_name(typ)})>"

    class_name = f"Null({_name(typ)})"
    return NULL(class_name, (typ,), {
        "__display__": class_name,
        "__null__": _null(typ)
    })

@cache
def NotNull(typ):
    from typed.mods.types.base import TYPE
    if not isinstance(typ, TYPE):
        raise TypeError(
            "Wrong type in 'NotNull' factory: \n"
            f" ==> '{_name(typ)}': has unexpected type\n"
             "     [expected_type] TYPE"
            f"     [received_type] {_name(TYPE(typ))}"
        )

    class NULL(TYPE(typ)):
        def __instancecheck__(cls, instance):
            return instance != _null(typ)
        def __repr__(cls):
            return f"<NotNull({_name(typ)})>"

    class_name = f"NotNull({_name(typ)})"
    return NULL(class_name, (typ,), {
        "__display__": class_name,
        "__null__": None
    })

@cache
def Enum(typ, *values):
    """
    Build the 'valued-type':
        > 'x' is an object of 'Enum(typ, *values)' iff:
            1. isinstance(x, typ) is True
            2. x in {v1, v2, ...}
        > Enum(typ, ...) is a subclass of 'typ'
        > Enum(typ) = Null(typ)
        > Enum() = Nill
    """
    if typ and not values:
        try:
            return Null(typ)
        except Exception:
            from typed.mods.types.base import Nill
            return Nill

    from typed.mods.types.base import TYPE
    if typ and values:
        if not isinstance(typ, TYPE):
            raise TypeError(
                "Wrong type in Enum factory: \n"
                f" ==> {_name(typ)}: has unexpected type\n"
                 "     [expected_type] Typed\n"
                f"     [received_type] {_name(TYPE(typ))}"
            )
        for value in values:
            if not isinstance(value, typ):
                raise TypeError(
                    "Wrong type in Enum factory: \n"
                    f" ==> {value}: has unexpected type\n"
                    f"     [expected_type] {_name(typ)}\n"
                    f"     [received_type] {_name(TYPE(value))}"
                )
    values_set = set(values)
    class ENUM(TYPE(typ)):
        def __instancecheck__(cls, instance):
            return isinstance(instance, cls.__base_type__) and instance in cls.__allowed_values__

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, cls.__base_type__)

    class_name = f"Enum({_name(typ)}; {_name_list(*values)})"

    Enum_ = ENUM(class_name, (typ,), {
        "__display__": class_name,
        '__base_type__': typ,
        '__allowed_values__': values_set,
    })

    Enum_.__null__ = _null(typ) if isinstance(_null(typ), Enum_) else None
    return Enum_

@cache
def Single(x):
    """
    Build the 'singleton-type':
        > the only object of 'Single(x)' is 'x'
        > 'Single(x)' is a subclass of 'TYPE(x)'
    """
    from typed.mods.types.base import TYPE
    t = TYPE(x)

    class SINGLE(TYPE(t)):
        def __instancecheck__(cls, instance):
            return TYPE(instance) is t and instance == cls.__value__

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, t)

    class_name = f"Single({_name(x)})"
    return SINGLE(class_name, (t,), {
        "__display__": class_name,
        '__value__': x,
        '__null__': x
    })
Singleton = Single

@cache
def Len(typ, size):
    """
    Build a 'sized-type'.
        > An object of 'Len(X, size)' is an object
        > 'x' of 'X such that 'len(x) == size'.
        1. Valid only for sized types and size >= 0
        2. 'Len(typ, 0)' is 'Null(typ)'
    """
    from typed.mods.types.base import TYPE
    if not isinstance(typ, TYPE):
        raise TypeError(
            "Wrong type in Len factory: \n"
            f" ==> {_name(typ)}: has unexpected type\n"
            f"     [expected_type] TYPE\n"
            f"     [received_type] {_name(TYPE(typ))}"
        )
    from typed.mods.factories.meta import ATTR
    if not isinstance(typ, ATTR('__len__')):
        raise TypeError(
            "Wrong type in Len factory: \n"
            f" ==> {_name(typ)}: has unexpected type\n"
            f"     [expected_type] ATTR('__len__')\n"
            f"     [received_type] {_name(TYPE(typ))}"
        )
    from typed.mods.types.base import Int
    if not isinstance(size, Int):
        raise TypeError(
            "Wrong type in Len factory: \n"
            f" ==> {size}: has unexpected type\n"
            f"     [expected_type] Nat\n"
            f"     [received_type] {_name(TYPE(size))}"
        )
    if size < 0:
        raise TypeError(
            "Wrong type in Enum factory: \n"
            f" ==> {size}: has unexpected type\n"
            f"     [expected_type] Nat\n"
            f"     [received_type] {_name(TYPE(size))}"
        )
    if size == 0:
        return Null(typ)

    class LEN(TYPE(typ)):
        def __instancecheck__(cls, instance):
            return isinstance(instance, typ) and len(instance) == cls.__len__

        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, typ)

    class_name = f"Len({_name(typ)}; {size})"
    return LEN(class_name, (typ,), {
        "__display__": class_name,
        '__len__': size,
        '__null__': _null(typ) if size == 0 else None
    })

@cache
def Maybe(*types):
    """
    Build a 'maybe-type'.
        > An object of `Maybe(X, Y, ..)`
        > is `None` or an object of `X`, `Y`, ...
    """
    from typed.mods.types.base import TYPE
    for typ in types:
        if not isinstance(typ, TYPE):
            raise TypeError(
                "Wrong type in Len factory: \n"
                f" ==> {_name(typ)}: has unexpected type\n"
                f"     [expected_type] TYPE\n"
                f"     [received_type] {_name(TYPE(typ))}"
            )
    types_ = (TYPE(typ) for typ in types)
    class MAYBE(*types_):
        def __instancecheck__(cls, instance):
            if any(isinstance(instance, typ) for typ in types) or instance is None:
                return True
            return False
    class_name = f"Maybe({_name_list(*types)})"
    return MAYBE(class_name, types, {
        "__display__": class_name,
        "__null__": _null_from_list(*types)
    })
