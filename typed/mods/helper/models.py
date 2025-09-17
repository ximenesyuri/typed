import sys
from typed.mods.meta.models import _MODEL_FACTORY_
from typed.mods.types.base import TYPE

class OPTIONAL:
    def __init__(self, typ, default_value):
        self.type = typ
        self.default_value = default_value

MODEL_FACTORY = _MODEL_FACTORY_('MODEL_FACTORY', (TYPE,), {})

def _ensure_iterable_conditions(conditions):
    if callable(conditions):
        return [conditions]
    if isinstance(conditions, (list, tuple)):
        if all(callable(f) for f in conditions):
            return list(conditions)
    raise TypeError("__conditions__ must be a callable or a list/tuple of callables")

def _ordered_keys(attributes_and_types, optional_defaults):
    return [k for k, _ in attributes_and_types] + list(optional_defaults.keys())

def _process_extends(__extends__):
    extended_models = []
    if __extends__ is not None:
        if isinstance(__extends__, list):
            extended_models.extend(__extends__)
        else:
            extended_models.append(__extends__)
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
        if isinstance(value, OPTIONAL):
            processed_attributes_and_types.append((key, value.type))
            optional_attributes_and_defaults[key] = value
        elif isinstance(value, type) or hasattr(value, '__instancecheck__'):
            processed_attributes_and_types.append((key, value))
            required_attribute_keys.add(key)
        else:
            raise TypeError(
                f"All argument values must be types or OptionalArg instances. Invalid type for '{key}': {type(value)}"
            )
    return tuple(processed_attributes_and_types), required_attribute_keys, optional_attributes_and_defaults

def _optional(type_hint, default, is_nullable):
    from typed.mods.factories.generics import Maybe
    from typed.mods.helper.models import OPTIONAL
    if isinstance(type_hint, OPTIONAL):
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
        return Optional(Maybe(type_hint), None)

def _attach_model_attrs(child_model, parent_models):
    child_model.extends     = tuple(parent_models)
    child_model.extended_by = ()

    child_model.is_model     = True
    child_model.is_exact     = False
    child_model.is_ordered   = False
    child_model.is_rigid     = False
    child_model.is_optional  = False
    child_model.is_mandatory = False

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

    for parent in parent_models:
        try:
            prev = getattr(parent, 'extended_by', ())
            if not isinstance(prev, tuple):
                prev = tuple(prev)
            parent.extended_by = prev + (child_model,)
        except Exception:
            pass
