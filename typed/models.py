from typing import Union, Type, List, Any
from typed.mods.types.base import Json
from typed.mods.helper.helper import _get_type_display_name
from typed.mods.helper.models import (
    _Optional,
    _MODEL,
    _EXACT,
    _CONDITIONAL
)

def Optional(typ: Type, default_value: Any):
    if not isinstance(typ, type) and not hasattr(typ, '__instancecheck__'):
        raise TypeError(f"'{_get_type_display_name(typ)}' is not a type.")
    if not isinstance(default_value, typ):
        raise TypeError(
            f"Error while defining optional type:\n"
            f" ==> '{default_value}': has wrong type\n" +
            f"     [received_type]: '{_get_type_display_name(type(default_value))}'\n" +
            f"     [expected_type]: '{_get_type_display_name(typ)}'"
        )
    return _Optional(typ, default_value)

def Model(__extends__: Type[Json] | List[Type[Json]] = None, **kwargs: Type) -> Type[Json]:
    """
    Build a 'model' which is a subclass of Json with support for optional arguments.
        > An object 'x' is an instance of Model(arg1: Type1, arg2: Type2 = default_value, ...) iff:
            1. isinstance(x, Json) is True
            2. x is a dictionary
            3. x.get(arg1) has type Type1
            4. If arg2 is present in x, x.get(arg2) has type Type2, otherwise the default value is used implicitly.

    Concatenation of Models is supported.
    """
    extended_models = []
    if __extends__ is not None:
        if isinstance(__extends__, list):
            extended_models.extend(__extends__)
        else:
            extended_models.append(__extends__)

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

        for key, value in kwargs.items():
            if key in combined_kwargs:
                raise TypeError(f"Attribute '{key}' defined in both extended models and the new model definition.")
            combined_kwargs[key] = value

        kwargs = combined_kwargs

    if not kwargs:
        return dict

    if not all(isinstance(key, str) for key in kwargs.keys()):
        raise TypeError("All arguments to Model must be strings representing attribute names.")

    processed_attributes_and_types = []
    required_attribute_keys = set()
    optional_attributes_and_defaults = {}

    for key, value in kwargs.items():
        if isinstance(value, _Optional):
            optional_attributes_and_defaults[key] = value
        elif isinstance(value, type) or hasattr(value, '__instancecheck__'):
            processed_attributes_and_types.append((key, value))
            required_attribute_keys.add(key)
        else:
            raise TypeError(f"All argument values to Model must be types or OptionalArg instances. Invalid type for '{key}': {type(value).__name__}")

    attributes_and_types = tuple(processed_attributes_and_types)

    class ModelInstance(dict):
        _defined_required_attributes: dict = {}
        _defined_optional_attributes: dict = {}
        _defined_keys: set = set()

        def __init__(self, *args, **data):
            # We explicitly handle data from kwargs.
            # *args could be passed if someone does MyModel({"x":1}), which we discourage.
            # Our __call__ method ensures data comes through kwargs.
            super().__init__() # Initialize the underlying dictionary

            # Set default values for optional attributes first
            for key, wrapper in self.__class__._defined_optional_attributes.items():
                # Directly assign to dict, not via __setattr__, to avoid recursion during init
                super().__setitem__(key, wrapper.default_value)

            # Now, update with provided data. This will overwrite defaults.
            # Use the validated incoming data.
            # We rely on the _Model.__call__ method to have already validated these types.
            # So, we can directly set them into the dictionary using super().__setitem__.
            # If we used self.__setattr__ here, it would re-run type checks during init,
            # which is fine, but needs to be careful not to trigger recursion.
            for key, value in data.items():
                self.__setattr__(key, value) # Use __setattr__ to ensure validation and dict update

            # Check for missing required attributes (although `Instance` should cover this)
            for req_key in self.__class__._defined_required_attributes.keys():
                if req_key not in self:
                    # This implies a severe error if Instance passed.
                    raise TypeError(f"Missing required attribute '{req_key}' during {self.__class__.__name__} initialization.") 

        def __getattr__(self, name: str):
            if name in self._defined_keys:
                if name in self:
                    return self[name]
                elif name in self._defined_optional_attributes:
                    return self._defined_optional_attributes[name].default_value
            try:
                return object.__getattribute__(self, name) # Try to get from actual instance attributes (like _defined_keys)
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


        def __setattr__(self, name: str, value: Any):
            if name in self._defined_required_attributes:
                expected_type = self._defined_required_attributes[name]
                if not (isinstance(value, expected_type) or
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(
                        f"Attempted to set '{name}' to value '{value}' with type '{_get_type_display_name(type(value))}', "
                        f"but expected type '{_get_type_display_name(expected_type)}'."
                    )
                self[name] = value
            elif name in self._defined_optional_attributes:
                expected_type = self._defined_optional_attributes[name].type
                if not (isinstance(value, expected_type) or
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(
                        f"Attempted to set '{name}' to value '{value}' with type '{_get_type_display_name(type(value))}', "
                        f"but expected type '{_get_type_display_name(expected_type)}'."
                    )
                self[name] = value
            else:
                object.__setattr__(self, name, value)

        def __delattr__(self, name: str):
            if name in self._defined_required_attributes:
                raise AttributeError(f"Cannot delete required attribute '{name}' from a '{self.__class__.__name__}' object.")
            elif name in self._defined_optional_attributes:
                if name in self:
                    del self[name]
                else:
                    raise AttributeError(f"'{name}' not found in '{self.__class__.__name__}' object.")
            else:
                object.__delattr__(self, name)


    class _Model(type(Json)):
        def __new__(cls, name, bases, dct):
            new_type = super().__new__(cls, name, bases, dct) # Create the actual type (which inherits ModelInstance)
            setattr(new_type, '_defined_required_attributes', dict(dct.get('_initial_attributes_and_types', ())))
            setattr(new_type, '_defined_optional_attributes', dct.get('_initial_optional_attributes_and_defaults', {}))
            setattr(new_type, '_defined_keys',
                    set(dict(dct.get('_initial_attributes_and_types', ())).keys()) |
                    set(dct.get('_initial_optional_attributes_and_defaults', {}).keys()))
            setattr(new_type, '_required_attributes_and_types', dct.get('_initial_attributes_and_types', ()))
            setattr(new_type, '_required_attribute_keys', dct.get('_initial_required_attribute_keys', set()))
            setattr(new_type, '_optional_attributes_and_defaults', dct.get('_initial_optional_attributes_and_defaults', {}))
            return new_type

        def __init__(cls, name, bases, dct):
            for key in ['_initial_attributes_and_types', '_initial_required_attribute_keys', '_initial_optional_attributes_and_defaults']:
                if key in dct:
                    del dct[key]
            super().__init__(name, bases, dct)

        def __instancecheck__(cls, instance: Any) -> bool:
            if not isinstance(instance, dict):
                return False

            required_attributes_and_types_dict = dict(getattr(cls, '_required_attributes_and_types', ()))
            required_attribute_keys = getattr(cls, '_required_attribute_keys', set())
            optional_attributes_and_defaults = getattr(cls, '_optional_attributes_and_defaults', {})

            for req_key, expected_type in required_attributes_and_types_dict.items():
                if req_key not in instance:
                    return False
                attr_value = instance[req_key]
                type_is_correct = False
                if isinstance(attr_value, expected_type):
                    type_is_correct = True
                else:
                    checker = getattr(expected_type, '__instancecheck__', None)
                    if callable(checker):
                        if checker(attr_value):
                            type_is_correct = True
                if not type_is_correct:
                    return False

            for attr_name, wrapper in optional_attributes_and_defaults.items():
                if attr_name in instance:
                    attr_value = instance[attr_name]
                    expected_type = wrapper.type
                    type_is_correct = False
                    if isinstance(attr_value, expected_type):
                        type_is_correct = True
                    else:
                        checker = getattr(expected_type, '__instancecheck__', None)
                        if callable(checker):
                            if checker(attr_value):
                                type_is_correct = True
                    if not type_is_correct:
                        return False
            return True

        def __subclasscheck__(cls, subclass: Type) -> bool:
            if not hasattr(subclass, '_required_attributes_and_types') or \
               not hasattr(subclass, '_required_attribute_keys') or \
               not hasattr(subclass, '_optional_attributes_and_defaults'):
                return False

            if not isinstance(subclass, type):
                return False

            cls_required_attrs = dict(getattr(cls, '_required_attributes_and_types', ()))
            subclass_required_attrs = dict(getattr(subclass, '_required_attributes_and_types', ()))
            cls_required_keys = getattr(cls, '_required_attribute_keys', set())
            subclass_required_keys = getattr(subclass, '_required_attribute_keys', set())
            cls_optional_attrs_defaults = getattr(cls, '_optional_attributes_and_defaults', {})
            subclass_optional_attrs_defaults = getattr(subclass, '_optional_attributes_and_defaults', {})
            cls_optional_keys = set(cls_optional_attrs_defaults.keys())

            if not cls_required_keys.issubset(subclass_required_keys):
                return False

            if not (cls_required_keys | cls_optional_keys).issubset(subclass_required_keys | set(subclass_optional_attrs_defaults.keys())):
                return False

            for attr_name, parent_type in cls_required_attrs.items():
                if attr_name in subclass_required_attrs:
                    subclass_type = subclass_required_attrs[attr_name]
                    if not (isinstance(subclass_type, type) and issubclass(subclass_type, parent_type)) and \
                       not (hasattr(parent_type, '__subclasscheck__') and parent_type.__subclasscheck__(subclass_type)):
                        return False
                elif attr_name in subclass_optional_attrs_defaults:
                    return False

            for attr_name, parent_wrapper in cls_optional_attrs_defaults.items():
                parent_type = parent_wrapper.type
                if attr_name in subclass_required_attrs:
                    subclass_type = subclass_required_attrs[attr_name]
                    if not (isinstance(subclass_type, type) and issubclass(subclass_type, parent_type)) and \
                       not (hasattr(parent_type, '__subclasscheck__') and parent_type.__subclasscheck__(subclass_type)):
                        return False
                elif attr_name in subclass_optional_attrs_defaults:
                    subclass_wrapper = subclass_optional_attrs_defaults[attr_name]
                    subclass_type = subclass_wrapper.type
                    subclass_default_value = subclass_wrapper.default_value

                    if not (isinstance(subclass_type, type) and issubclass(subclass_type, parent_type)) and \
                       not (hasattr(parent_type, '__subclasscheck__') and parent_type.__subclasscheck__(subclass_type)):
                        return False
                    if not (isinstance(subclass_default_value, parent_type) or
                            (hasattr(parent_type, '__instancecheck__') and parent_type.__instancecheck__(subclass_default_value))):
                        return False
                else:
                    return False

            return True

        def __call__(cls, entity: Any = None, **kwargs):
            if entity is not None and kwargs:
                raise TypeError("Cannot provide both 'entity' (dictionary) and keyword arguments simultaneously.")

            # Prepare data to initialize the ModelInstance
            if entity is None:
                entity_dict = kwargs
            else:
                # If entity is a dict, we need to convert it to kwargs for __init__
                # This ensures consistent handling.
                if not isinstance(entity, dict):
                    raise TypeError(f"Expected a dictionary or keyword arguments, got {type(entity)}")
                entity_dict = entity.copy() # Use a copy to avoid modifying the original

            # Validate the entity_dict against the model definition before creating an instance
            if not cls.__instancecheck__(entity_dict):
                # When __instancecheck__ returns False, it doesn't provide errors.
                # We need to call Instance function separately which provides detailed error messages.
                Instance(entity_dict, cls) # This will raise TypeError with details if not valid

            # Create an instance of the specific ModelInstance subclass (cls)
            # The ModelInstance.__init__ will handle populating the dictionary
            # and setting attributes, including defaults for optional ones.
            # Pass **entity_dict directly to __init__
            obj = cls.__new__(cls, **entity_dict) # Pass kwargs to __new__ if it handles them
            # However, typical __new__ for simple classes accepts args, kwargs and forwards them to object.__new__
            # For dict subclasses, __new__ usually takes an optional single dict or kwargs.
            # Let's keep __new__ simple and pass to __init__
            obj.__init__(**entity_dict) # Call __init__ with validated data
            return obj 


    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, _Optional) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    class_name = f"Model({args_str})"
    return _Model(class_name, (ModelInstance,), {
        '_initial_attributes_and_types': attributes_and_types,
        '_initial_required_attribute_keys': required_attribute_keys,
        '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults
    })

def Exact(__extends__: Type[Json] | List[Type[Json]] = None, **kwargs: Type) -> Type[Json]:
    """
    Build an 'exact model' with support for optional arguments.
        > 'x' is an object of 'Exact(arg1=Type1, arg2=Type2 = default_value, ...)' iff:
            1. isinstance(x, Json) is True
            2. The set of keys in x is exactly the set of required argument keys.
            3. x.get(arg1) is of type Type1 (for required args)
            4. x.get(arg2) is of type Type2 (for optional args present in x)

    Concatenation of Exacts is supported.
    """
    extended_models = []
    if __extends__ is not None:
        if isinstance(__extends__, list):
            extended_models.extend(__extends__)
        else:
            extended_models.append(__extends__)

        combined_kwargs = {}
        for extended_model in extended_models:
            if not hasattr(extended_model, '_required_attributes_and_types') or not hasattr(extended_model, '_optional_attributes_and_defaults'):
                raise TypeError(f"Element in __extends__ must be a Model or Exact type, got {type(extended_model)}")

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
        for key, value in kwargs.items():
            if key in combined_kwargs:
                raise TypeError(f"Attribute '{key}' defined in both extended models and the new model definition.")
            combined_kwargs[key] = value
        kwargs = combined_kwargs

    if not kwargs:
        return dict

    if not all(isinstance(key, str) for key in kwargs.keys()):
        raise TypeError("All arguments to Exact must be strings representing attribute names.")

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
            raise TypeError(f"All argument values to Exact must be types or OptionalArg instances. Invalid type for '{key}': {type(value)}")

    attributes_and_types = tuple(processed_attributes_and_types)

    class ExactInstance(dict):
        _defined_required_attributes: dict = {}
        _defined_optional_attributes: dict = {}
        _defined_keys: set = set()
        _all_possible_keys: set = set()

        def __init__(self, **data):
            super().__init__()
            for key, wrapper in self.__class__._defined_optional_attributes.items():
                self[key] = wrapper.default_value

            for key, value in data.items():
                self.__setattr__(key, value)

        def __getattr__(self, name: str):
            if name in self._defined_keys:
                if name in self:
                    return self[name]
                elif name in self._defined_optional_attributes:
                    return self._defined_optional_attributes[name].default_value
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        def __setattr__(self, name: str, value: Any):
            if name in self._defined_required_attributes:
                expected_type = self._defined_required_attributes[name]
                if not (isinstance(value, expected_type) or
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(
                        f"Attempted to set '{name}' to value '{value}' with type '{_get_type_display_name(type(value))}', "
                        f"but expected type '{_get_type_display_name(expected_type)}'."
                    )
                self[name] = value
            elif name in self._defined_optional_attributes:
                expected_type = self._defined_optional_attributes[name].type
                if not (isinstance(value, expected_type) or
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(
                        f"Attempted to set '{name}' to value '{value}' with type '{_get_type_display_name(type(value))}', "
                        f"but expected type '{_get_type_display_name(expected_type)}'."
                    )
                self[name] = value
            else:
                object.__setattr__(self, name, value)

        def __delattr__(self, name: str):
            if name in self._defined_required_attributes:
                raise AttributeError(f"Cannot delete required attribute '{name}' from a '{self.__class__.__name__}' object.")
            elif name in self._defined_optional_attributes:
                if name in self:
                    del self[name]
                else:
                    raise AttributeError(f"'{name}' not found in '{self.__class__.__name__}' object.")
            else:
                object.__delattr__(self, name)


    class _Exact(type(Json)):
        def __new__(cls, name, bases, dct):
            new_type = super().__new__(cls, name, bases, dct)
            setattr(new_type, '_defined_required_attributes', dict(dct.get('_initial_attributes_and_types', ())))
            setattr(new_type, '_defined_optional_attributes', dct.get('_initial_optional_attributes_and_defaults', {}))
            setattr(new_type, '_defined_keys',
                    set(dict(dct.get('_initial_attributes_and_types', ())).keys()) |
                    set(dct.get('_initial_optional_attributes_and_defaults', {}).keys()))
            setattr(new_type, '_all_possible_keys', dct.get('_initial_all_possible_keys', set()))

            setattr(new_type, '_required_attributes_and_types', dct.get('_initial_attributes_and_types', ()))
            setattr(new_type, '_required_attribute_keys', dct.get('_initial_required_attribute_keys', set()))
            setattr(new_type, '_optional_attributes_and_defaults', dct.get('_initial_optional_attributes_and_defaults', {}))

            return new_type

        def __init__(cls, name, bases, dct):
            for key in ['_initial_attributes_and_types', '_initial_required_attribute_keys', '_initial_optional_attributes_and_defaults', '_initial_all_possible_keys']:
                if key in dct:
                    del dct[key]
            super().__init__(name, bases, dct)

        def __instancecheck__(cls, instance: Any) -> bool:
            if not isinstance(instance, dict):
                return False

            required_attributes_and_types_dict = dict(getattr(cls, '_required_attributes_and_types', ()))
            required_attribute_keys = getattr(cls, '_required_attribute_keys', set())
            optional_attributes_and_defaults = getattr(cls, '_optional_attributes_and_defaults', {})
            instance_keys = set(instance.keys())
            all_possible_keys = required_attribute_keys | set(optional_attributes_and_defaults.keys())

            if instance_keys != all_possible_keys:
                return False

            if not required_attribute_keys.issubset(instance_keys):
                return False

            for attr_name, attr_value in instance.items():
                if attr_name in required_attributes_and_types_dict:
                    expected_type = required_attributes_and_types_dict[attr_name]
                    type_is_correct = False
                    if isinstance(attr_value, expected_type):
                        type_is_correct = True
                    else:
                        checker = getattr(expected_type, '__instancecheck__', None)
                        if callable(checker):
                            if checker(attr_value):
                                type_is_correct = True
                    if not type_is_correct:
                        return False
                elif attr_name in optional_attributes_and_defaults:
                    expected_type = optional_attributes_and_defaults[attr_name].type
                    type_is_correct = False
                    if isinstance(attr_value, expected_type):
                        type_is_correct = True
                    else:
                        checker = getattr(expected_type, '__instancecheck__', None)
                        if callable(checker):
                            if checker(attr_value):
                                type_is_correct = True
                    if not type_is_correct:
                        return False
                else:
                    return False
            return True

        def __subclasscheck__(cls, subclass):
            if not hasattr(subclass, '_required_attributes_and_types') or not hasattr(subclass, '_required_attribute_keys') or not hasattr(subclass, '_optional_attributes_and_defaults'):
                return False
            if not isinstance(subclass, type):
                return False

            cls_required_attrs = dict(getattr(cls, '_required_attributes_and_types', ()))
            subclass_required_attrs = dict(getattr(subclass, '_required_attributes_and_types', ()))
            cls_required_keys = getattr(cls, '_required_attribute_keys', set())
            subclass_required_keys = getattr(subclass, '_required_attribute_keys', set())
            cls_optional_attrs_defaults = getattr(cls, '_optional_attributes_and_defaults', {})
            subclass_optional_attrs_defaults = getattr(subclass, '_optional_attributes_and_defaults', {})
            cls_optional_keys = set(cls_optional_attrs_defaults.keys())
            subclass_optional_keys = set(subclass_optional_attrs_defaults.keys())

            if (cls_required_keys | cls_optional_keys) != (subclass_required_keys | subclass_optional_keys):
                return False

            if not cls_required_keys.issubset(subclass_required_keys):
                return False

            for attr_name in cls_optional_keys:
                if attr_name not in subclass_optional_keys:
                    return False

                parent_wrapper = cls_optional_attrs_defaults[attr_name]
                parent_type = parent_wrapper.type
                subclass_wrapper = subclass_optional_attrs_defaults[attr_name]
                subclass_type = subclass_wrapper.type
                subclass_default_value = subclass_wrapper.default_value

                if not (isinstance(subclass_type, type) and issubclass(subclass_type, parent_type)) and \
                   not (hasattr(parent_type, '__subclasscheck__') and parent_type.__subclasscheck__(subclass_type)):
                    return False

                if not (isinstance(subclass_default_value, parent_type) or
                        (hasattr(parent_type, '__instancecheck__') and parent_type.__instancecheck__(subclass_default_value))):
                    return False

            for attr_name in cls_required_keys:
                parent_type = cls_required_attrs[attr_name]
                if attr_name not in subclass_required_attrs:
                    return False

                subclass_type = subclass_required_attrs[attr_name]

                if not (isinstance(subclass_type, type) and issubclass(subclass_type, parent_type)) and \
                   not (hasattr(parent_type, '__subclasscheck__') and parent_type.__subclasscheck__(subclass_type)):
                    return False

            return True

        def __call__(cls, entity: Any = None, **kwargs):
            if entity is not None and kwargs:
                raise TypeError("Cannot provide both 'entity' (dictionary) and keyword arguments simultaneously.")

            if entity is None:
                entity_dict = kwargs
            else:
                entity_dict = entity

            if not cls.__instancecheck__(entity_dict):
                Instance(entity_dict, cls)

            obj = cls.__new__(cls)
            obj.__init__(**entity_dict)
            return obj

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, _Optional) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    class_name = f"Exact({args_str})"

    return _Exact(class_name, (ExactInstance,), {
        '_initial_attributes_and_types': attributes_and_types,
        '_initial_required_attribute_keys': required_attribute_keys,
        '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults,
        '_initial_all_possible_keys': required_attribute_keys | set(optional_attributes_and_defaults.keys())
    })

def Conditional(__conditionals__: List[str], __extends__=None, **kwargs: Type) -> Type[Json]:
    UnderlyingModel = __extends__ if __extends__ and not kwargs else Model(__extends__, **kwargs)

    conds = __conditionals__ if isinstance(__conditionals__, (list, tuple)) else [__conditionals__]
    for cond in conds:
        domain = getattr(cond, 'domain', None)
        if domain is None:
            raise AttributeError(f"Conditional function {cond} must have a .domain attribute set to the underlying Model")
        if not issubclass(UnderlyingModel, domain):
            raise TypeError(f"Condition {cond} has domain {domain}, expected {UnderlyingModel}")

    class ConditionalInstance(UnderlyingModel):
        def __init__(self, **data):
            super().__init__(**data)

    class _Conditional(type(UnderlyingModel)):
        def __new__(cls, name, bases, dct):
            new_type = super().__new__(cls, name, (ConditionalInstance,), dct)
            return new_type

        def __init__(cls, name, bases, dct):
            super().__init__(name, bases, dct)

        def __instancecheck__(cls, instance):
            if not isinstance(instance, dict):
                return False

            if not isinstance(instance, UnderlyingModel):
                return False

            from typed.mods.types.base import BoolFuncType
            for cond in conds:
                if not isinstance(cond, BoolFuncType):
                    raise TypeError(f"Condition '{cond.__name__}' is not a Boolean typed function.")
                if not cond(instance):
                    return False
            return True

        def __subclasscheck__(cls, subclass):
            if not issubclass(subclass, UnderlyingModel):
                return False
            return True

        def __call__(cls, entity: Any = None, **kwargs):
            if entity is not None and kwargs:
                raise TypeError("Cannot provide both 'entity' (dictionary) and keyword arguments simultaneously.")
            if entity is None:
                entity_dict = kwargs
            else:
                entity_dict = entity

            Instance(entity_dict, UnderlyingModel)

            from typed.mods.types.base import BoolFuncType
            for cond in conds:
                if not isinstance(cond, BoolFuncType):
                    if not issubclass(UnderlyingModel, cond.domain):
                        raise TypeError(
                            f" ==> '{cond.__name__}': has wrong domain type.\n"
                            f"     [received_type]: '{_get_type_display_name(cond.domain)}'\n"
                            f"     [expected_type]: '{_get_type_display_name(UnderlyingModel)}'"
                        )
                    raise TypeError(
                        f" ==> '{cond.__name__}': is not a Boolean typed function."
                    )
                if not cond(entity_dict):
                    raise TypeError(
                        f" Boolean check failed"
                        f" ==> {cond.__name__}: expected True, received False for {entity_dict}"
                    )

            obj = cls.__new__(cls)
            obj.__init__(**entity_dict)

            return obj

    conds_str = ', '.join(getattr(cond, '__name__', repr(cond)) for cond in conds)
    class_name = f"Conditional({conds_str})"
    CondModel = type.__new__(_Conditional, class_name, (UnderlyingModel,), {})
    return CondModel

def Instance(entity: dict, model: Type[Json]) -> Json:
    """
    Checks if an entity (dictionary) is an instance of a given model.
    If it is, the entity is returned. Otherwise, a TypeError is raised with details.
    """
    model_metaclass = type(model)


    if not isinstance(model, (type(_MODEL), type(_EXACT), type(_CONDITIONAL))):
        raise TypeError(f"'{getattr(model, '__name__', str(model))}' not of Model, Exact or Conditional type. Received type: {type(model).__name__}.")

    if not isinstance(entity, dict):
        raise TypeError(f"'{repr(entity)}': not of Json type (expected dict-like). Received type: {type(entity).__name__}.")

    if isinstance(entity, model):
        return entity

    model_name = getattr(model, '__name__', str(model))

    required_attributes_and_types_raw = dict(getattr(model, '_required_attributes_and_types', ()))
    required_attribute_keys = getattr(model, '_required_attribute_keys', set())
    optional_attributes_and_defaults = getattr(model, '_optional_attributes_and_defaults', {})

    errors = []

    for k in required_attribute_keys:
        if k not in entity:
            errors.append(f"\t ==> '{k}': missing required attribute.")

    all_defined_attributes_for_check = required_attributes_and_types_raw.copy()
    for k, wrapper in optional_attributes_and_defaults.items():
        all_defined_attributes_for_check[k] = wrapper.type

    for attr_name, expected_type in all_defined_attributes_for_check.items():
        if attr_name in entity:
            actual_value = entity[attr_name]
            type_is_correct = False
            if isinstance(actual_value, expected_type):
                type_is_correct = True
            else:
                checker = getattr(expected_type, '__instancecheck__', None)
                if callable(checker):
                    if checker(actual_value):
                        type_is_correct = True

            if not type_is_correct:
                errors.append(
                    f"\t ==> '{attr_name}': has a wrong type.\n" +
                    f"\t     [received_type]: '{_get_type_display_name(type(actual_value))}'\n" +
                    f"\t     [expected_type]: '{_get_type_display_name(expected_type)}'"
                )
    if model_metaclass.__name__ == "_Exact":
        all_expected_keys = required_attribute_keys | set(optional_attributes_and_defaults.keys())
        extra_keys = set(entity.keys()) - all_expected_keys
        if extra_keys:
            errors.append(f"\t ==> Extra attributes found: {', '.join(sorted(extra_keys))}.")

    if model_metaclass.__name__ == "_Conditional":
        conds = getattr(model, '__conditionals_list', [])
        if not conds and hasattr(model, '__bases__') and model.__bases__ and issubclass(model.__bases__[0], Json):
            pass


    if errors:
        raise TypeError(
            f"'{repr(entity)}' is not an instance of model '{_get_type_display_name(model)}':\n"
            + "\n".join(errors)
        )
    return entity


MODEL = _MODEL('MODEL', (type, ), {})
EXACT = _EXACT('EXACT', (type, ), {})
CONDITIONAL = _CONDITIONAL('CONDITIONAL', (type, ), {})


def Forget(model: Type[Json], entries: list) -> Type[Json]:
    if not isinstance(model, type(_MODEL)): # Check against the metaclass type
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

def model(_cls=None, *, extends=None):
    def wrap(cls):
        annotations = cls.__annotations__
        kwargs = {name: type_hint for name, type_hint in annotations.items()}
        return_model = Model(__extends__=extends, **kwargs)
        return_model.__name__ = cls.__name__
        return_model.__qualname__ = cls.__qualname__
        return_model.__module__ = cls.__module__
        return_model.__doc__ = cls.__doc__
        return return_model
    if _cls is None: return wrap
    else: return wrap(_cls)

def exact(_cls=None, *, extends=None):
    def wrap(cls):
        annotations = cls.__annotations__
        kwargs = {name: type_hint for name, type_hint in annotations.items()}
        exact_model = Exact(__extends__=extends, **kwargs)
        exact_model.__name__ = cls.__name__
        exact_model.__qualname__ = cls.__qualname__
        exact_model.__module__ = cls.__module__
        exact_model.__doc__ = cls.__doc__
        return exact_model
    if _cls is None: return wrap
    else: return wrap(_cls)

def conditional(*, conditions, extends=None):
    def wrap(cls):
        annotations = cls.__annotations__
        kwargs = {name: type_hint for name, type_hint in annotations.items()}
        cond_model = Conditional(__conditionals__=conditions, __extends__=extends, **kwargs)
        cond_model.__name__ = cls.__name__
        cond_model.__qualname__ = cls.__qualname__
        cond_model.__module__ = cls.__module__
        cond_model.__doc__ = cls.__doc__
        return cond_model
    return wrap
