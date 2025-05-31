from typing import Type, Any, Dict, Tuple
from typed.mods.types.base import Json, Str, Int
from typed.mods.helper_models import _OptionalWrapper

def Optional(type: Type, default_value: Any):
    if not isinstance(type, type) and not hasattr(type, '__instancecheck__'):
        raise TypeError(f"OptionalArg type must be a type or have an __instancecheck__ method, got {type}.")
    if not isinstance(default_value, type):
        if hasattr(type, '__instancecheck__') and not type.__instancecheck__(default_value):
            raise TypeError(f"Default value {default_value} is not an instance of {getattr(type, '__name__', str(type))}.")
        elif isinstance(type, type) and not isinstance(default_value, type):
            raise TypeError(f"Default value {default_value} is not an instance of {getattr(type, '__name__', str(type))}.")
    return _OptionalWrapper(type, default_value)
   
class BaseModelInstanceWrapper(Json):
    """A wrapper class for validated model data providing attribute access."""
    def __init__(self, data: Dict[str, Any], model_type: Type):
        if not isinstance(data, dict):
            raise TypeError(f"Instance data must be a dictionary, got {type(data).__name__}")

        if not isinstance(model_type, type) or (not issubclass(type(model_type), type(AnyModel)) and type(model_type) is not type(AnyModel)):
            pass

        self._data = data
        self._model_type = model_type

    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        else:
            optional_attrs = getattr(self._model_type, '_optional_attributes_and_defaults', {})
            if name in optional_attrs:
                return optional_attrs[name]
            raise AttributeError(f"'{self._model_type.__name__}' object has no attribute '{name}'")

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data or key in getattr(self._model_type, '_optional_attributes_and_defaults', {})

    def keys(self):
        all_keys = set(self._data.keys()) | set(getattr(self._model_type, '_optional_attributes_and_defaults', {}).keys())
        return all_keys

    def values(self):
        return [self[key] for key in self.keys()]

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._data:
            return self._data[key]
        optional_attrs = getattr(self._model_type, '_optional_attributes_and_defaults', {})
        if key in optional_attrs:
            return optional_attrs[key]
        return default

    def __len__(self):
        return len(self.keys())

    def __eq__(self, other):
        if isinstance(other, BaseModelInstanceWrapper):
            return self._data == other._data and self._model_type == other._model_type
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

class _BaseModelMeta(type(Json)):
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        setattr(new_class, '_initial_attributes_and_types', dct.get('_initial_attributes_and_types', ()))
        setattr(new_class, '_initial_required_attribute_keys', dct.get('_initial_required_attribute_keys', set()))
        setattr(new_class, '_initial_optional_attributes_and_defaults', dct.get('_initial_optional_attributes_and_defaults', {}))
        if '_initial_all_possible_keys' in dct:
            setattr(new_class, '_initial_all_possible_keys', dct['_initial_all_possible_keys'])
        return new_class

    def __init__(cls, name, bases, dct):
        if '_initial_attributes_and_types' in dct:
            del dct['_initial_attributes_and_types']
        if '_initial_required_attribute_keys' in dct:
            del dct['_initial_required_attribute_keys']
        if '_initial_optional_attributes_and_defaults' in dct:
            del dct['_initial_optional_attributes_and_defaults']
        if '_initial_all_possible_keys' in dct:
            del dct['_initial_all_possible_keys']
        super().__init__(name, bases, dct)

    def __subclasscheck__(cls, subclass: Type) -> bool:
        if Json in cls.__bases__ and subclass is Json:
            return True

        if not isinstance(subclass, type):
            return False

        if not hasattr(subclass, '_initial_attributes_and_types'):
            return super().__subclasscheck__(subclass)

        cls_attrs = dict(getattr(cls, '_initial_attributes_and_types', ()))
        subclass_attrs = dict(getattr(subclass, '_initial_attributes_and_types', ()))
        cls_required_keys = getattr(cls, '_initial_required_attribute_keys', set())
        subclass_required_keys = getattr(subclass, '_initial_required_attribute_keys', set())
        cls_optional_attrs_defaults = dict(getattr(cls, '_initial_optional_attributes_and_defaults', {}))
        subclass_optional_attrs_defaults = dict(getattr(subclass, '_initial_optional_attributes_and_defaults', {}))
        cls_optional_keys = set(cls_optional_attrs_defaults.keys())
        subclass_optional_keys = set(subclass_optional_attrs_defaults.keys())

        if not cls_required_keys.issubset(subclass_required_keys):
            return False

        for attr_name in cls_required_keys:
            parent_type = cls_attrs.get(attr_name)
            subclass_type = subclass_attrs.get(attr_name)

            if parent_type is None or subclass_type is None:
                return False

            if hasattr(parent_type, '__subclasscheck__'):
                if not parent_type.__subclasscheck__(subclass_type):
                    return False
            elif isinstance(parent_type, type) and isinstance(subclass_type, type):
                if not issubclass(subclass_type, parent_type):
                    return False
            else:
                if parent_type != subclass_type:
                   return False

        for attr_name in cls_optional_keys:
            if attr_name in subclass_optional_keys:
                parent_optional_info = cls_optional_attrs_defaults.get(attr_name)
                subclass_optional_info = subclass_optional_attrs_defaults.get(attr_name)

                parent_type = parent_optional_info.type
                subclass_type = subclass_optional_info.type

                if hasattr(parent_type, '__subclasscheck__'):
                    if not parent_type.__subclasscheck__(subclass_type):
                        return False
                elif isinstance(parent_type, type) and isinstance(subclass_type, type):
                    if not issubclass(subclass_type, parent_type):
                        return False
                else:
                    if parent_type != subclass_type:
                       return False

                subclass_default_value = subclass_optional_info.default_value
                if hasattr(parent_type, '__instancecheck__'):
                    if not parent_type.__instancecheck__(subclass_default_value):
                        return False
                elif isinstance(parent_type, type):
                    if not isinstance(subclass_default_value, parent_type):
                        return False
        return True

    def __instancecheck__(cls, instance: Any) -> bool:
        if isinstance(instance, BaseModelInstanceWrapper):
            return True
        data_to_check = instance
        if not isinstance(data_to_check, dict):
            return False
        required_attribute_keys = getattr(cls, '_initial_required_attribute_keys', set())
        optional_attributes_and_defaults = getattr(cls, '_initial_optional_attributes_and_defaults', {})
        defined_attrs_types = dict(getattr(cls, '_initial_attributes_and_types', ()))
        if not required_attribute_keys.issubset(data_to_check.keys()):
            return False
        for attr_name, attr_value in data_to_check.items():
            if attr_name in defined_attrs_types:
                expected_type = defined_attrs_types[attr_name]
                if isinstance(expected_type, type):
                    if not isinstance(attr_value, expected_type):
                        return False
                elif hasattr(expected_type, '__instancecheck__'):
                    if not expected_type.__instancecheck__(attr_value):
                        return False
        return True 

def Model(**kwargs: Type) -> Type[Json]:
    """
    Build a 'model' which is a subclass of Json with support for optional arguments.
        > An object 'x' is an instance of Model(arg1: Type1, arg2: Type2 = default_value, ...) iff:
            1. isinstance(x, Json) is True
            2. x is a dictionary
            3. x.get(arg1) has type Type1
            4. If arg2 is present in x, x.get(arg2) has type Type2, otherwise the default value is used implicitly.

    Concatenation of Models is supported.
    """
    if not kwargs:
        return dict

    if not all(isinstance(key, str) for key in kwargs.keys()):
        raise TypeError("All arguments to Model must be strings representing attribute names.")

    processed_attributes_and_types = []
    required_attribute_keys = set()
    optional_attributes_and_defaults = {}

    for key, value in kwargs.items():
        if isinstance(value, _OptionalWrapper):
            processed_attributes_and_types.append((key, value.type))
            optional_attributes_and_defaults[key] = value
        elif isinstance(value, type) or hasattr(value, '__instancecheck__'):
            processed_attributes_and_types.append((key, value))
            required_attribute_keys.add(key)
        else:
            raise TypeError(f"All argument values to Model must be types or OptionalArg instances. Invalid type for '{key}': {type(value)}")

    attributes_and_types = tuple(processed_attributes_and_types)
 
    class __Model(_BaseModelMeta):
        def __call__(cls, data: dict) -> BaseModelInstanceWrapper:
            """Validate the data against the model and return a wrapper."""
            if not isinstance(data, cls):
                required_attribute_keys = getattr(cls, '_initial_required_attribute_keys', set())
                optional_attributes_and_defaults = getattr(cls, '_initial_optional_attributes_and_defaults', {})
                defined_attrs_types = dict(getattr(cls, '_initial_attributes_and_types', ()))

                if not isinstance(data, dict):
                    raise TypeError(f"Data for '{cls.__name__}' must be an instance of '{cls.__name__}' or a dictionary, got {type(data).__name__}.")

                missing_required = required_attribute_keys - data.keys()
                if missing_required:
                    raise TypeError(f"Data is missing required keys for '{cls.__name__}': {list(missing_required)}")
 
                type_mismatches = []
                for attr_name, attr_value in data.items():
                    if attr_name in defined_attrs_types:
                        expected_type = defined_attrs_types[attr_name]

                        if isinstance(expected_type, type):
                            if not isinstance(attr_value, expected_type):
                                type_mismatches.append(f"'{attr_name}': expected instance of '{getattr(expected_type, '__name__', str(expected_type))}', got instance of '{type(attr_value).__name__}'")
                        elif hasattr(expected_type, '__instancecheck__'):
                            if not expected_type.__instancecheck__(attr_value):
                                type_mismatches.append(f"'{attr_name}': expected instance check pass for '{getattr(expected_type, '__name__', str(expected_type))}', but it failed for instance of '{type(attr_value).__name__}'")
                if type_mismatches:
                    raise TypeError(f"Data type mismatches for '{cls.__name__}': {', '.join(type_mismatches)}")
                pass

            if isinstance(data, BaseModelInstanceWrapper):
                return data

            return BaseModelInstanceWrapper(data, cls)


    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, _OptionalWrapper) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    class_name = f"Model({args_str})"
    model_class = __Model(class_name, (dict,), {
        '_initial_attributes_and_types': attributes_and_types,
        '_initial_required_attribute_keys': required_attribute_keys,
        '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults
    })
    return model_class


def ExactModel(**kwargs: Type) -> Type[Json]:
    """
    Build an 'exact model' with support for optional arguments.
        > 'x' is an object of 'ExactModel(arg1=Type1, arg2=Type2 = default_value, ...)' iff:
            1. isinstance(x, Json) is True
            2. The set of keys in x is exactly the set of required argument keys plus any optional keys present in x.
            3. x.get(arg1) is of type Type1 (for required args)
            4. x.get(arg2) is of type Type2 (for optional args present in x)

    Concatenation of ExactModels is supported.
    """
    if not kwargs:
        return dict

    if not all(isinstance(key, str) for key in kwargs.keys()):
        raise TypeError("All arguments to ExactModel must be strings representing attribute names.")

    processed_attributes_and_types = []
    required_attribute_keys = set()
    optional_attributes_and_defaults = {}

    for key, value in kwargs.items():
        if isinstance(value, _OptionalWrapper):
            processed_attributes_and_types.append((key, value.type))
            optional_attributes_and_defaults[key] = value
        elif isinstance(value, type) or hasattr(value, '__instancecheck__'):
            processed_attributes_and_types.append((key, value))
            required_attribute_keys.add(key)
        else:
            raise TypeError(f"All argument values to ExactModel must be types or OptionalArg instances. Invalid type for '{key}': {type(value)}")

    attributes_and_types = tuple(processed_attributes_and_types)
    all_defined_keys = required_attribute_keys | set(optional_attributes_and_defaults.keys())

    class __ExactModel(_BaseModelMeta):

        def __call__(cls, data: dict) -> BaseModelInstanceWrapper:
            """Validate the data against the model and return a wrapper."""
            if not isinstance(data, cls):
                required_attribute_keys = getattr(cls, '_initial_required_attribute_keys', set())
                optional_attributes_and_defaults = getattr(cls, '_initial_optional_attributes_and_defaults', {})
                defined_attrs_types = dict(getattr(cls, '_initial_attributes_and_types', ()))
                all_possible_keys = required_attribute_keys | set(optional_attributes_and_defaults.keys())

                if not isinstance(data, dict):
                    raise TypeError(f"Data for '{cls.__name__}' must be an instance of '{cls.__name__}' or a dictionary, got {type(data).__name__}.")

                instance_keys = set(data.keys())
                missing_required = instance_keys - all_possible_keys
                extraneous_keys = instance_keys - all_possible_keys

                errors = []
                if missing_required:
                    missing_required_actual = required_attribute_keys - instance_keys
                    if missing_required_actual:
                        errors.append(f"has missing required keys: {list(missing_required_actual)}")

                if extraneous_keys:
                    errors.append(f"has extraneous keys: {list(extraneous_keys)}")

                if errors:
                    raise TypeError(f"Data keys for '{cls.__name__}' {', and '.join(errors)}.")
                type_mismatches = []
                for attr_name, attr_value in data.items():
                    if attr_name in defined_attrs_types:
                        expected_type = defined_attrs_types.get(attr_name)

                        if isinstance(expected_type, type):
                            if not isinstance(attr_value, expected_type):
                                type_mismatches.append(f"'{attr_name}': expected instance of '{getattr(expected_type, '__name__', str(expected_type))}', got instance of '{type(attr_value).__name__}'")
                        elif hasattr(expected_type, '__instancecheck__'):
                            if not expected_type.__instancecheck__(attr_value):
                                type_mismatches.append(f"'{attr_name}': expected instance check pass for '{getattr(expected_type, '__name__', str(expected_type))}', but it failed for instance of '{type(attr_value).__name__}'")
                if type_mismatches:
                    raise TypeError(f"Data type mismatches for '{cls.__name__}': {', '.join(type_mismatches)}")
                pass

            if isinstance(data, BaseModelInstanceWrapper):
                return data

            return BaseModelInstanceWrapper(data, cls)

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, _OptionalWrapper) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    class_name = f"ExactModel({args_str})"

    exact_model_class = __ExactModel(class_name, (dict,), {
        '_initial_attributes_and_types': attributes_and_types,
        '_initial_required_attribute_keys': required_attribute_keys,
        '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults,
        '_initial_all_possible_keys': all_defined_keys
    })
    return exact_model_class

AnyModel = Model()

def Instance(entity: dict, model: Type) -> BaseModelInstanceWrapper:
    """
    Validates a dictionary entity against a Model or ExactModel and
    returns a BaseModelInstanceWrapper for attribute access.
    """
    if not isinstance(model, type) or (type(model) is not type(AnyModel) and not issubclass(type(model), type(AnyModel)) ):
        raise TypeError(f"'{getattr(model, '__name__', str(model))}' not of Model or ExactModel types. Received type: {type(model).__name__}.")

    return model(entity)


