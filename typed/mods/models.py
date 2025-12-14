from typed.mods.types.base import TYPE, Str, Dict, List, Bool, Any
from typed.mods.factories.base import Union
from typed.mods.factories.generics import Maybe
from typed.mods.helper.helper import _name
from typed.mods.meta.models import (
    _MODEL_FACTORY_,
    _MODEL_, _EXACT_, _ORDERED_, _RIGID_,
    _OPTIONAL_, _MANDATORY_,
    MODEL_INSTANCE, MODEL_META,
    EXACT_INSTANCE, EXACT_META,
    ORDERED_INSTANCE, ORDERED_META,
    RIGID_INSTANCE, RIGID_META
)
from typed.mods.helper.models import (
    _Optional,
    MODEL_FACTORY,
    _ordered_keys,
    _attach_model_attrs,
    _process_extends,
    _merge_attrs,
    _attrs,
)
from typed.mods.decorators import typed

MODEL_METATYPES = Union(_MODEL_, _EXACT_, _ORDERED_, _RIGID_, _MODEL_FACTORY_)
MODEL     = _MODEL_('MODEL', (TYPE,), {'__display__': 'MODEL'})
EXACT     = _EXACT_('EXACT', (MODEL,), {'__display__': 'EXACT'})
ORDERED   = _ORDERED_('ORDERED', (MODEL, ), {'__display__': 'ORDERED'})
RIGID     = _RIGID_('RIGID', (EXACT, ORDERED, ), {'__display__': 'RIGID'})
OPTIONAL  = _OPTIONAL_('OPTIONAL', (MODEL,), {'__display__': 'OPTIONAL'})
MANDATORY = _MANDATORY_('MANDATORY', (MODEL,), {'__display__': 'MANDATORY'})

def Optional(typ, default_value=None):
    if not isinstance(typ, TYPE):
        raise TypeError(f"'{_name(typ)}' is not a type.")
    if default_value is None:
        return _Optional(typ, None)
    if not isinstance(default_value, typ):
        raise TypeError(
            f"Error while defining optional type:\n"
            f" ==> '{default_value}': has wrong type\n"
            f"     [expected_type]: '{_name(typ)}'\n"
            f"     [received_type]: '{_name(TYPE(default_value))}'"
        )
    return _Optional(typ, default_value)

@typed
def Model(
    __extends__:    Maybe(List)=None,
    __conditions__: Maybe(List)=None,
    __exact__:      Bool=False,
    __ordered__:    Bool=False,
    __rigid__:      Bool=False,
    **kwargs:       Dict
) -> MODEL:

    if __rigid__:
        return Rigid(__extends__=__extends__, __conditions__=__conditions__, **kwargs)
    if __exact__:
        return Exact(__extends__=__extends__, __conditions__=__conditions__, **kwargs)
    if __ordered__:
        return Ordered(__extends__=__extends__, __conditions__=__conditions__, **kwargs)

    extended_models = _process_extends(__extends__)
    if extended_models:
        kwargs = _merge_attrs(extended_models, kwargs)
    if not kwargs and not extended_models:
        bases = (MODEL_INSTANCE, MODEL_FACTORY, MODEL)
        attributes_and_types = ()
        required_attribute_keys = set()
        optional_attributes_and_defaults = {}
        conditions = []
        ordered_keys = []
        class_name = "Model()"
        new_model = MODEL_META(
            class_name,
            bases,
            {
                '_initial_attributes_and_types': attributes_and_types,
                '_initial_required_attribute_keys': required_attribute_keys,
                '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults,
                '_initial_conditions': conditions,
                '_initial_ordered_keys': ordered_keys,
            }
        )
        _attach_model_attrs(new_model, ())
        new_model.__display__ = class_name
        from typed.mods.helper.null import _null_model
        new_model.__null__ = _null_model(new_model)
        new_model.is_model = True
        return new_model

    for key in kwargs.keys():
        if not isinstance(key, Str):
            raise TypeError(f"Model keys must be strings. Got: {_name(TYPE(key))}")

    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _attrs(kwargs)
    conditions = list(__conditions__) if __conditions__ else []
    ordered_keys = _ordered_keys(attributes_and_types, optional_attributes_and_defaults)

    args_str = ", ".join(f"{key}: {_name(value)}" for key, value in kwargs.items())
    class_name = f"Model({args_str})"

    bases = tuple(extended_models) + (MODEL_INSTANCE, MODEL_FACTORY, MODEL)

    new_model = MODEL_META(
        class_name,
        bases,
        {
            '_initial_attributes_and_types': attributes_and_types,
            '_initial_required_attribute_keys': required_attribute_keys,
            '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults,
            '_initial_conditions': conditions,
            '_initial_ordered_keys': ordered_keys
        }
    )
    _attach_model_attrs(new_model, extended_models)
    new_model.__display__ = class_name
    from typed.mods.helper.null import _null_model
    new_model.__null__ = _null_model(new_model)
    new_model.is_model = True
    return new_model

@typed
def Exact(
    __extends__   : Maybe(List)=None,
    __conditions__: Maybe(List)=None,
    **kwargs      : Dict
    ) -> EXACT:

    extended_models = _process_extends(__extends__)
    if extended_models:
        kwargs = _merge_attrs(extended_models, kwargs)

    for key in kwargs.keys():
        if not isinstance(key, Str):
            raise TypeError(f"Model keys must be strings. Got: {_name(TYPE(key))}")

    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _attrs(kwargs)
    all_possible_keys = set(kwargs.keys())
    conditions = list(__conditions__) if __conditions__ else []

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" for key, value in kwargs.items())
    class_name = f"Exact({args_str})"

    bases = tuple(extended_models) + (EXACT_INSTANCE, MODEL_FACTORY, EXACT)
    new_model = EXACT_META(
        class_name,
        bases,
        {
            '_initial_attributes_and_types': attributes_and_types,
            '_initial_required_attribute_keys': required_attribute_keys,
            '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults,
            '_initial_all_possible_keys': all_possible_keys,
            '_initial_conditions': conditions,
        }
    )

    _attach_model_attrs(new_model, extended_models)
    new_model.is_exact = True
    from typed.mods.helper.null import _null_model
    new_model.__null__ = _null_model(new_model)
    new_model.__display__ = class_name
    return new_model

@typed
def Ordered(
    __extends__:    Maybe(List)=None,
    __conditions__: Maybe(List)=None,
    **kwargs:       Dict
    ) -> ORDERED:

    extended_models = _process_extends(__extends__)
    if extended_models:
        kwargs = _merge_attrs(extended_models, kwargs)

    for key in kwargs.keys():
        if not isinstance(key, Str):
            raise TypeError(f"Model keys must be strings. Got: {_name(TYPE(key))}")

    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _attrs(kwargs)
    ordered_keys = _ordered_keys(attributes_and_types, optional_attributes_and_defaults)
    conditions = list(__conditions__) if __conditions__ else []

    args_str = ", ".join(f"{key}: {_name(value)}" for key, value in kwargs.items())
    class_name = f"Ordered({args_str})"

    bases = tuple(extended_models) + (ORDERED_INSTANCE, MODEL_FACTORY, ORDERED)
    new_model = ORDERED_META(
        class_name,
        bases,
        {
            '_initial_attributes_and_types': attributes_and_types,
            '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults,
            '_initial_ordered_keys': ordered_keys,
            '_initial_conditions': conditions,
        }
    )

    _attach_model_attrs(new_model, extended_models)
    new_model.is_ordered = True
    from typed.mods.helper.null import _null_model
    new_model.__null__ = _null_model(new_model)
    new_model.__display__ = class_name
    return new_model

@typed
def Rigid(
    __extends__:    Maybe(List)=None,
    __conditions__: Maybe(List)=None,
    **kwargs:       Dict
    ) -> RIGID:

    extended_models = _process_extends(__extends__)
    if extended_models:
        kwargs = _merge_attrs(extended_models, kwargs)

    for key in kwargs.keys():
        if not isinstance(key, Str):
            raise TypeError(f"Model keys must be strings. Got: {_name(TYPE(key))}")

    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _attrs(kwargs)
    ordered_keys = _ordered_keys(attributes_and_types, optional_attributes_and_defaults)
    conditions = list(__conditions__) if __conditions__ else []

    args_str = ", ".join(f"{key}: {_name(value)}" for key, value in kwargs.items())
    class_name = f"Rigid({args_str})"
    bases = tuple(extended_models) + (RIGID_INSTANCE, MODEL_FACTORY, RIGID)

    new_model = RIGID_META(
        class_name,
        bases,
        {
            '_initial_attributes_and_types': attributes_and_types,
            '_initial_required_attribute_keys': required_attribute_keys,
            '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults,
            '_initial_ordered_keys': ordered_keys,
            '_initial_conditions': conditions,
        }
    )

    _attach_model_attrs(new_model, extended_models)
    new_model.is_rigid = True
    new_model.is_ordered = True
    new_model.is_exact = True
    from typed.mods.helper.null import _null_model
    new_model.__null__ = _null_model(new_model)
    new_model.__display__ = class_name
    return new_model

@typed
def validate(entity: Dict, model: MODEL) -> Dict:
    model_name = getattr(model, '__name__', str(model))

    if entity in model:
        return entity

    required_attributes_and_types_raw = dict(getattr(model, '_required_attributes_and_types', ()))
    required_attribute_keys = list(getattr(model, '_required_attribute_keys', []))
    optional_attributes_and_defaults = getattr(model, '_optional_attributes_and_defaults', {})
    ordered_keys = list(getattr(model, '_ordered_keys', []))
    all_model_keys = set(required_attributes_and_types_raw.keys()) | set(optional_attributes_and_defaults.keys())

    errors = []

    if model in RIGID:
        entity_keys = list(entity.keys())
        if entity_keys != ordered_keys:
            errors.append(f" ==> Keys are {entity_keys}, expected {ordered_keys}.")
        else:
            for k in entity_keys:
                v = entity[k]
                if k in required_attributes_and_types_raw:
                    typ = required_attributes_and_types_raw[k]
                elif k in optional_attributes_and_defaults:
                    typ = optional_attributes_and_defaults[k].type
                else:
                    errors.append(f" ==> Unexpected attribute '{k}'.")
                    continue
                if not (v in typ):
                    errors.append(
                        f" ==> '{k}': wrong type.\n"
                        f"     [received_type]: '{_name(TYPE(v))}'\n"
                        f"     [expected_type]: '{_name(typ)}'"
                    )
        conds = getattr(model, '__conditions_list', [])
        for cond in conds:
            if not cond(entity):
                errors.append(f" ==> Condition {getattr(cond, '__name__', cond)} failed for {entity}")
        if errors:
            raise TypeError(f"{repr(entity)} is not a term of type {model_name}:\n" + "\n".join(errors))
        return entity

    elif model in ORDERED:
        entity_keys = list(entity.keys())
        K = len(entity_keys)
        model_prefix = ordered_keys[:K]
        if entity_keys != model_prefix:
            errors.append(f" ==> Keys {entity_keys} do not match expected prefix {model_prefix}.")

        for k in entity_keys:
            v = entity[k]
            if k in required_attributes_and_types_raw:
                typ = required_attributes_and_types_raw[k]
            elif k in optional_attributes_and_defaults:
                typ = optional_attributes_and_defaults[k].type
            else:
                errors.append(f" ==> Unexpected attribute '{k}'.")
                continue
            if not (v in typ):
                errors.append(
                    f" ==> '{k}': wrong type.\n"
                    f"     [received_type]: '{_name(TYPE(v))}'\n"
                    f"     [expected_type]: '{_name(typ)}'"
                )
        conds = getattr(model, '__conditions_list', [])
        for cond in conds:
            if not cond(entity):
                errors.append(f" ==> Condition {getattr(cond, '__name__', cond)} failed for {entity}")
        if errors:
            raise TypeError(f"{repr(entity)} is not a term of type {model_name}:\n" + "\n".join(errors))
        return entity

    elif model in EXACT:
        all_expected_keys = set(required_attribute_keys) | set(optional_attributes_and_defaults.keys())
        missing = all_expected_keys - set(entity.keys())
        extra = set(entity.keys()) - all_expected_keys
        if missing:
            for m in sorted(missing):
                errors.append(f" ==> '{m}' missing.")
        if extra:
            errors.append(f" ==> Extra attributes found: {', '.join(sorted(extra))}.")
        for k in all_expected_keys:
            if k in entity:
                v = entity[k]
                if k in required_attributes_and_types_raw:
                    typ = required_attributes_and_types_raw[k]
                elif k in optional_attributes_and_defaults:
                    typ = optional_attributes_and_defaults[k].type
                else:
                    errors.append(f" ==> Unexpected attribute '{k}'.")
                    continue
                if not (v in typ):
                    errors.append(
                        f" ==> '{k}': wrong type.\n"
                        f"     [received_type]: '{_name(TYPE(v))}'\n"
                        f"     [expected_type]: '{_name(typ)}'"
                    )
        conds = getattr(model, '__conditions_list', [])
        for cond in conds:
            if not cond(entity):
                errors.append(f" ==> Condition {getattr(cond, '__name__', cond)} failed for {entity}")
        if errors:
            raise TypeError(f"{repr(entity)} is not a term of type {model_name}:\n" + "\n".join(errors))
        return entity

    for k in required_attribute_keys:
        if k not in entity:
            errors.append(f" ==> '{k}' missing.")

    for attr_name, expected_type in required_attributes_and_types_raw.items():
        if attr_name in entity:
            v = entity[attr_name]
            if not (v in expected_type):
                errors.append(
                    f" ==> '{attr_name}': wrong type.\n"
                    f"     [received_type]: '{_name(TYPE(v))}'\n"
                    f"     [expected_type]: '{_name(expected_type)}'"
                )
    for attr_name, wrapper in optional_attributes_and_defaults.items():
        if attr_name in entity:
            v = entity[attr_name]
            if not (v in wrapper.type):
                errors.append(
                    f" ==> '{attr_name}': wrong type.\n"
                    f"     [received_type]: '{_name(TYPE(v))}'\n"
                    f"     [expected_type]: '{_name(wrapper.type)}'"
                )
    conds = getattr(model, '__conditions_list', [])
    for cond in conds:
        if not cond(entity):
            errors.append(f" ==> Condition {getattr(cond, '__name__', cond)} failed for {entity}")
    if errors:
        raise TypeError(f"{repr(entity)} is not a term of type {model_name}:\n" + "\n".join(errors))
    return entity

def drop(model, entries):
    if not isinstance(model, MODEL):
        raise TypeError(f"forget expects a Model-type. Got: {model}")

    required_keys = set(getattr(model, '_required_attribute_keys', set()))
    optional_keys = set(getattr(model, '_optional_attributes_and_defaults', {}).keys())
    all_keys = required_keys | optional_keys

    missing = [e for e in entries if e not in all_keys]
    if missing:
        raise ValueError(f"Entries not in model: {missing}")

    required_types = dict(getattr(model, '_required_attributes_and_types', ()))
    optional_types = getattr(model, '_optional_attributes_and_defaults', {})

    new_kwargs = {}

    for k in required_keys:
        if k not in entries:
            new_kwargs[k] = required_types[k]

    for k in optional_keys:
        if k not in entries:
            new_kwargs[k] = optional_types[k]
    return Model(**new_kwargs)

def model(_cls=None, *, extends=None, conditions=None, exact=False, ordered=False, rigid=False, nullable=False):
    def wrap(cls):
        all_extends = []
        if extends:
            if isinstance(extends, (list, tuple)):
                all_extends.extend(extends)
            else:
                all_extends.append(extends)

        for base in cls.__bases__:
            if getattr(base, 'is_model', False) and base not in all_extends:
                all_extends.append(base)

        annotations = getattr(cls, '__annotations__', {})
        is_nullable = getattr(cls, '__nullable__', nullable)
        kwargs = {}
        for name, type_hint in annotations.items():
            if isinstance(type_hint, _Optional):
                kwargs[name] = type_hint
            elif hasattr(cls, name):
                default = getattr(cls, name)
                kwargs[name] = Optional(type_hint, default)
            else:
                kwargs[name] = type_hint
        return_model = Model(
            __extends__=all_extends,
            __conditions__=conditions,
            __exact__=exact,
            __ordered__=ordered,
            __rigid__=rigid,
            **kwargs
        )
        return_model.__name__ = cls.__name__
        return_model.__qualname__ = cls.__qualname__
        return_model.__module__ = cls.__module__
        return_model.__doc__ = cls.__doc__
        return return_model
    if _cls is None:
        return wrap
    else:
        return wrap(_cls)

def exact(_cls=None, *, extends=None, conditions=None):
    def wrap(cls):
        all_extends = []
        if extends:
            if isinstance(extends, (list, tuple)):
                all_extends.extend(extends)
            else:
                all_extends.append(extends)

        for base in cls.__bases__:
            if getattr(base, 'is_model', False) and base not in all_extends:
                all_extends.append(base)

        annotations = cls.__annotations__
        kwargs = {name: type_hint for name, type_hint in annotations.items()}
        exact_model = Exact(__extends__=all_extends, __conditions__=conditions, **kwargs)
        exact_model.__name__ = cls.__name__
        exact_model.__qualname__ = cls.__qualname__
        exact_model.__module__ = cls.__module__
        exact_model.__doc__ = cls.__doc__
        return exact_model
    if _cls is None: return wrap
    else: return wrap(_cls)

def ordered(_cls=None, *, extends=None, conditions=None):
    def wrap(cls):
        all_extends = []
        if extends:
            if isinstance(extends, (list, tuple)):
                all_extends.extend(extends)
            else:
                all_extends.append(extends)

        for base in cls.__bases__:
            if getattr(base, 'is_model', False) and base not in all_extends:
                all_extends.append(base)

        annotations = cls.__annotations__
        kwargs = {name: type_hint for name, type_hint in annotations.items()}
        res = Ordered(__extends__=all_extends, __conditions__=conditions, **kwargs)
        res.__name__ = cls.__name__
        res.__qualname__ = cls.__qualname__
        res.__module__ = cls.__module__
        res.__doc__ = cls.__doc__
        return res
    if _cls is None: return wrap
    else: return wrap(_cls)

def rigid(_cls=None, *, extends=None, conditions=None):
    def wrap(cls):
        all_extends = []
        if extends:
            if isinstance(extends, (list, tuple)):
                all_extends.extend(extends)
            else:
                all_extends.append(extends)

        for base in cls.__bases__:
            if getattr(base, 'is_model', False) and base not in all_extends:
                all_extends.append(base)

        annotations = cls.__annotations__
        kwargs = {name: type_hint for name, type_hint in annotations.items()}
        res = Rigid(__extends__=all_extends, __conditions__=conditions, **kwargs)
        res.__name__ = cls.__name__
        res.__qualname__ = cls.__qualname__
        res.__module__ = cls.__module__
        res.__doc__ = cls.__doc__
        return res
    if _cls is None: return wrap
    else: return wrap(_cls)

def optional(_cls=None, *, extends=None, conditions=None, exact=False, ordered=False, rigid=False, nullable=False):
    def wrap(cls):
        parent_models = []
        for base in cls.__bases__:
            if getattr(base, 'is_model', False):
                parent_models.append(base)
        if extends:
            if isinstance(extends, (list, tuple)):
                parent_models += list(extends)
            else:
                parent_models.append(extends)

        seen = set()
        parent_models = [b for b in parent_models if not (b in seen or seen.add(b))]

        ann = getattr(cls, '__annotations__', {})
        from typed.mods.helper.models import _optional
        is_null = getattr(cls, '__nullable__', nullable)
        kwargs = {}
        for name, hint in ann.items():
            default = getattr(cls, name, None)
            kwargs[name] = _optional(hint, default, is_null)

        model_cls = Model(
            __extends__=parent_models,
            __conditions__=conditions,
            __exact__=exact,
            __ordered__=ordered,
            __rigid__=rigid,
            **kwargs
        )

        for a in ('__name__', '__qualname__', '__module__', '__doc__'):
            setattr(model_cls, a, getattr(cls, a, None))
        model_cls.is_optional = True
        model_cls.is_mandatory = False
        return model_cls

    if _cls is None:
        return wrap
    else:
        return wrap(_cls)

def mandatory(_cls=None, *, extends=None, conditions=None, exact=False, ordered=False, rigid=False):
    def wrap(cls):
        parent_models = []
        for base in cls.__bases__:
            if getattr(base, 'is_model', False):
                parent_models.append(base)
        if extends:
            if isinstance(extends, (list, tuple)):
                parent_models += list(extends)
            else:
                parent_models.append(extends)

        seen = set()
        parent_models = [b for b in parent_models if not (b in seen or seen.add(b))]

        ann = getattr(cls, '__annotations__', {})
        kwargs = {}
        for name, hint in ann.items():
            base = getattr(hint, 'type', hint)
            kwargs[name] = base

        model_cls = Model(
            __extends__=parent_models,
            __conditions__=conditions,
            __exact__=exact,
            __ordered__=ordered,
            __rigid__=rigid,
            **kwargs
        )

        for a in ('__name__', '__qualname__', '__module__', '__doc__'):
            setattr(model_cls, a, getattr(cls, a, None))
        model_cls.is_mandatory = True
        model_cls.is_optional = False
        return model_cls

    if _cls is None:
        return wrap
    else:
        return wrap(_cls)

@typed
def eval(model: MODEL, **attrs: Dict) -> MODEL:
    """
    Return a new model derived from `model` where attributes provided in `attrs`
    are fixed to the given values (i.e. turned into optional attributes with
    those values as defaults). The returned model Y behaves such that:
      Y(x1, x2, ...) == X(x1, x2, ..., attr1=value1, ...)
    """
    if not getattr(model, 'is_model', False):
        raise TypeError(f"eval expects a Model-type. Got: {model}")

    attrs_tuple = tuple(getattr(model, '_required_attributes_and_types', ()))
    opt_wrappers = dict(getattr(model, '_optional_attributes_and_defaults', {}))

    for name, val in attrs.items():
        if name not in (k for k, _ in attrs_tuple):
            raise ValueError(f"Attribute '{name}' not present in model '{getattr(model, '__name__', str(model))}'")
        expected_type = next((t for k, t in attrs_tuple if k == name), None)
        if expected_type is None:
            raise ValueError(f"Could not determine expected type for attribute '{name}'")

        ok = False
        try:
            if isinstance(val, expected_type):
                ok = True
        except Exception:
            pass
        if not ok:
            checker = getattr(expected_type, '__instancecheck__', None)
            if not (callable(checker) and checker(val)):
                raise TypeError(
                    f"Error while evaluating model:\n"
                    f" ==> '{name}': has wrong type\n"
                    f"     [expected_type]: '{_name(expected_type)}'\n"
                    f"     [received_value]: '{val}'\n"
                    f"     [received_type]: '{_name(TYPE(val))}'"
                )

    new_kwargs = {}
    for key, typ in attrs_tuple:
        if key in attrs:
            new_kwargs[key] = Optional(typ, attrs[key])
        else:
            if key in opt_wrappers:
                new_kwargs[key] = opt_wrappers[key]
            else:
                new_kwargs[key] = typ

    extends = getattr(model, 'extends', None)
    conds = getattr(model, '__conditions_list', None)
    __extends__ = list(extends) if extends else None
    __conditions__ = list(conds) if conds else None

    if model in RIGID:
        return Rigid(__extends__=__extends__, __conditions__=__conditions__, **new_kwargs)
    if model in EXACT:
        return Exact(__extends__=__extends__, __conditions__=__conditions__, **new_kwargs)
    if model in ORDERED:
        return Ordered(__extends__=__extends__, __conditions__=__conditions__, **new_kwargs)

    return Model(__extends__=__extends__, __conditions__=__conditions__, **new_kwargs)


@typed
def value(model: MODEL, attr: Str) -> Any:
    ###
    # TODO: improve to allow inner attributes:
    #       value(model, 'x.y.z')
    ###
    for k, v in model.optional_attrs.items():
        if attr == k:
            return v['default']

