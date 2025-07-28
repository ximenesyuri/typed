class _Optional:
    def __init__(self, typ, default_value):
        self.type = typ
        self.default_value = default_value

class _ModelFactory(type):
    def __instancecheck__(cls, instance):
        return cls.__instancecheck__(instance)

    def __subclasscheck__(cls, subclass):
        return cls.__subclasscheck__(subclass)

    def __call__(cls, *args, **kwargs):
        if len(args) > 1:
            raise TypeError(f"{cls.__name__}() takes at most one positional argument (got {len(args)})")
        if args and kwargs:
            raise TypeError("Cannot provide both a positional argument (dict/entity) and keyword arguments simultaneously.")
        if args:
            entity = args[0]
            if not isinstance(entity, dict):
                raise TypeError(f"Expected a dictionary or keyword arguments, got {type(entity)}")
            entity_dict = entity.copy()
        else:
            entity_dict = kwargs
        if not cls.__instancecheck__(entity_dict):
            from typed.models import Instance
            Instance(entity_dict, cls)
        obj = cls.__new__(cls)
        obj.__init__(**entity_dict)
        return obj

ModelFactory = _ModelFactory('ModelFactory', (), {})

def _ensure_iterable_conditions(conditions):
    if callable(conditions):
        return [conditions]
    if isinstance(conditions, (list, tuple)):
        if all(callable(f) for f in conditions):
            return list(conditions)
    raise TypeError("__conditions__ must be a callable or a list/tuple of callables")

def _get_keys_in_defined_order(attributes_and_types, optional_defaults):
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
    """ Merges extended model attributes and new attributes """
    combined_kwargs = {}
    for extended_model in extended_models:
        if not hasattr(extended_model, '_required_attributes_and_types') or not hasattr(extended_model, '_optional_attributes_and_defaults'):
            raise TypeError(f"Element in __extends__ must be a Model or Exact type, got {type(extended_model).__name__}")

        extended_attributes_and_types = dict(getattr(extended_model, '_required_attributes_and_types', ()))
        extended_optional_attributes_and_defaults = getattr(extended_model, '_optional_attributes_and_defaults', {})

        for key, value_type in extended_attributes_and_types.items():
            if key in combined_kwargs:
                raise TypeError(f"Attribute '{key}' defined in multiple extended models.")
            combined_kwargs[key] = value_type

        for key, value_wrapper in extended_optional_attributes_and_defaults.items():
            if key in combined_kwargs:
                raise TypeError(f"Attribute '{key}' defined in multiple extended models.")
            combined_kwargs[key] = value_wrapper

    for key, value in new_kwargs.items():
        if key in combined_kwargs:
            raise TypeError(f"Attribute '{key}' defined in both extended models and the new model definition.")
        combined_kwargs[key] = value
    return combined_kwargs

def _collect_attributes(kwargs):
    processed_attributes_and_types = []
    required_attribute_keys = set()
    optional_attributes_and_defaults = {}
    for key, value in kwargs.items():
        if isinstance(value, _Optional):
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

class _MODEL(type):
    def __instancecheck__(self, instance):
        t = type(instance)
        cls = instance.__class__ if not isinstance(instance, type) else instance
        return type(cls).__name__ == "_Model"

class _EXACT(type):
    def __instancecheck__(self, instance):
        t = type(instance)
        cls = instance.__class__ if not isinstance(instance, type) else instance
        return type(cls).__name__ == "_Exact"

class _ORDERED(type):
    def __instancecheck__(self, instance):
        t = type(instance)
        cls = instance.__class__ if not isinstance(instance, type) else instance
        return type(cls).__name__ == "_Ordered"

class _RIGID(type):
    def __instancecheck__(self, instance):
        t = type(instance)
        cls = instance.__class__ if not isinstance(instance, type) else instance
        return type(cls).__name__ == "_Rigid"
