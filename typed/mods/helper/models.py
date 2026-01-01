import json
from functools import lru_cache as cache
from typed.mods.meta.models import _MODEL_FACTORY_
from typed.mods.types.base import TYPE
from typed.mods.helper.helper import _name

class _Optional:
    def __init__(self, typ, default_value):
        self.type = typ
        self.default_value = default_value
        self.__display__ = f"Optional({_name(typ)}, {default_value})"

MODEL_FACTORY = _MODEL_FACTORY_('MODEL_FACTORY', (TYPE,), {})

def _ensure_iterable_conditions(conditions):
    if callable(conditions):
        return [conditions]
    if isinstance(conditions, (list, tuple)):
        if all(callable(f) for f in conditions):
            return list(conditions)
    raise TypeError("__conditions__ must be a callable or a list/tuple of callables")

def _ordered_keys(attributes_and_types, optional_defaults):
    return [k for k, _ in attributes_and_types]

def _materialize_if_lazy(model):
    if getattr(model, "__lazy_model__", False):
        materialize = getattr(model, "_materialize", None)
        if callable(materialize):
            try:
                return materialize()
            except Exception:
                return model
    return model

def _process_extends(__extends__):
    extended_models = []
    if __extends__ is not None:
        if isinstance(__extends__, list):
            extended_models.extend(__extends__)
        else:
            extended_models.append(__extends__)

    extended_models = [_materialize_if_lazy(m) for m in extended_models]
    return extended_models

def _merge_attrs(extended_models, new_kwargs):
    combined = {}

    for parent in extended_models:
        parent_required = dict(getattr(parent, '_required_attributes_and_types', ()))
        parent_optional = getattr(parent, '_optional_attributes_and_defaults', {})

        for k, opt in parent_optional.items():
            if k not in combined:
                combined[k] = opt

        for k, typ in parent_required.items():
            if k not in parent_optional and k not in combined:
                combined[k] = typ

    combined.update(new_kwargs)
    return combined

def _attrs(kwargs):
    processed_attributes_and_types = []
    required_attribute_keys = set()
    optional_attributes_and_defaults = {}
    for key, value in kwargs.items():
        if isinstance(value, _Optional):
            processed_attributes_and_types.append((key, value.type))
            optional_attributes_and_defaults[key] = value
        elif isinstance(value, TYPE) or hasattr(value, '__instancecheck__'):
            processed_attributes_and_types.append((key, value))
            required_attribute_keys.add(key)
        else:
            raise TypeError(
                f"All argument values must be types or OptionalArg instances. Invalid type for '{key}': {type(value)}"
            )
    return tuple(processed_attributes_and_types), required_attribute_keys, optional_attributes_and_defaults

def _optional(type_hint, default, is_nullable):
    from typed.mods.factories.generics import Maybe
    if isinstance(type_hint, _Optional):
        return type_hint

    from typed.models import Optional
    if is_nullable:
        if default is not None:
            return Optional(type_hint, default)
        try:
            from typed import null
            return Optional(type_hint, null(type_hint))
        except Exception:
            try:
                return Optional(type_hint, type_hint())
            except Exception:
                return Optional(type_hint, None)
    else:
        if default is not None:
            return Optional(Maybe(type_hint), default)
        return Optional(Maybe(type_hint), None)

def _attach_model_attrs(child_model, parent_models):
    if not hasattr(child_model, 'extends'):
        child_model.extends = tuple(parent_models)
        child_model.extended_by = ()
        child_model.is_model = True
        child_model.is_exact = False
        child_model.is_ordered = False
        child_model.is_rigid = False
        child_model.is_optional = False
        child_model.is_mandatory = False

        for parent in parent_models:
            try:
                prev = getattr(parent, 'extended_by', ())
                if not isinstance(prev, tuple):
                    prev = tuple(prev)
                parent.extended_by = prev + (child_model,)
            except Exception:
                pass

    reqs = getattr(child_model, '_defined_required_attributes', {})
    opts = getattr(child_model, '_defined_optional_attributes', {})

    all_meta = {}
    for name, typ in reqs.items():
        all_meta[name] = {
            'type':     typ,
            'optional': False,
            'default':  None
        }
    for name, wrapper in opts.items():
        all_meta[name] = {
            'type':     wrapper.type,
            'optional': True,
            'default':  wrapper.default_value
        }

    child_model.attrs = all_meta

    child_model.optional_attrs = {
        name: meta
        for name, meta in all_meta.items()
        if meta['optional']
    }

    child_model.mandatory_attrs = {
        name: meta
        for name, meta in all_meta.items()
        if not meta['optional']
    }

def _update_model_attr(cls, name, value):
    current_kwargs = {}
    ordered_keys_list = list(getattr(cls, '_ordered_keys', []))
    req_attrs = getattr(cls, '_defined_required_attributes', {})
    opt_attrs = getattr(cls, '_defined_optional_attributes', {})

    current_keys = set(ordered_keys_list)

    if name not in current_keys:
        ordered_keys_list.append(name)
    for k in ordered_keys_list:
        if k == name:
            current_kwargs[k] = value
        elif k in req_attrs:
            current_kwargs[k] = req_attrs[k]
        elif k in opt_attrs:
            current_kwargs[k] = opt_attrs[k]

    new_attrs_tuple, new_req_keys, new_opt_attrs = _attrs(current_kwargs)
    new_ordered_keys = _ordered_keys(new_attrs_tuple, new_opt_attrs)

    type.__setattr__(cls, '_required_attributes_and_types', new_attrs_tuple)
    type.__setattr__(cls, '_required_attribute_keys', new_req_keys)
    type.__setattr__(cls, '_optional_attributes_and_defaults', new_opt_attrs)
    type.__setattr__(cls, '_ordered_keys', new_ordered_keys)

    new_req_attrs_dict = {k: v for k, v in new_attrs_tuple if k in new_req_keys}
    type.__setattr__(cls, '_defined_required_attributes', new_req_attrs_dict)
    type.__setattr__(cls, '_defined_optional_attributes', new_opt_attrs)
    type.__setattr__(cls, '_defined_keys', set(new_ordered_keys))

    if hasattr(cls, '_all_possible_keys'):
        type.__setattr__(cls, '_all_possible_keys', set(new_ordered_keys))

    _attach_model_attrs(cls, getattr(cls, 'extends', ()))

def _to_json(obj):
    """
    Helper method to recursively convert an object to a JSON-serializable dictionary.
    """
    from typed.mods.models import MODEL
    json_dict = {}
    for key, value in obj.__dict__.items():
        if key.startswith('_'):
            continue
        if isinstance(value, MODEL):
            json_dict[key] = _to_json(value)
        elif isinstance(value, list) and all(isinstance(item, MODEL) for item in value):
            json_dict[key] = [_to_json(item) for item in value]
        elif isinstance(value, dict) and any(isinstance(item, MODEL) for item in value.values()):
            processed_dict = {}
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, MODEL):
                    processed_dict[sub_key] = _to_json(sub_value)
                else:
                    processed_dict[sub_key] = sub_value
            json_dict[key] = processed_dict
        else:
            try:
                json.dumps(value)
                json_dict[key] = value
            except TypeError:
                json_dict[key] = str(value)

    return json_dict


def _canonical_model_key(kind, extends, conditions, attrs):
    extends_key = tuple(extends or ())
    conditions_key = tuple(conditions or ())
    attrs_key = tuple(sorted(attrs.items(), key=lambda kv: kv[0]))
    return (kind, extends_key, conditions_key, attrs_key)
