from typing import Union, Type, List, Any, Dict
from typed.mods.types.base import Json
from typed.mods.helper.helper import _get_type_display_name
from typed.mods.helper.models import (
    _Optional,
    _ModelFactory,
    ModelFactory,
    _get_keys_in_defined_order,
    _process_extends,
    _merge_attrs,
    _collect_attributes,
    _MODEL,
    _EXACT,
    _ORDERED,
    _RIGID
)

MODEL_METATYPES = [type(_MODEL), type(_EXACT), type(_ORDERED), type(_RIGID), _ModelFactory]
MODEL   = _MODEL('MODEL', (type, ), {'__display__': 'MODEL'})
EXACT   = _EXACT('EXACT', (type, ), {'__display__': 'EXACT'})
ORDERED = _ORDERED('ORDERED', (type, ), {'__display__': 'ORDERED'})
RIGID   = _RIGID('RIGID', (type, ), {'__display__': 'RIGID'})

def Optional(typ: Type, default_value: Any=None):
    if not isinstance(typ, type) and not hasattr(typ, '__instancecheck__'):
        raise TypeError(f"'{_get_type_display_name(typ)}' is not a type.")
    if not default_value:
        try:
            from typed import null
            return _Optional(typ, null(typ))
        except Exception as e:
            try:
                return _Optional(typ, typ())
            except Exception as e:
                raise ValueError(
                    f"Error while defining optional value:\n"
                    f" ==> 'default_value' not provided and type '{_get_type_display_name(typ)}' has no null value."
                )
    if not isinstance(default_value, typ):
        raise TypeError(
            f"Error while defining optional type:\n"
            f" ==> '{default_value}': has wrong type\n"
            f"     [received_type]: '{_get_type_display_name(type(default_value))}'\n"
            f"     [expected_type]: '{_get_type_display_name(typ)}'"
        )
    return _Optional(typ, default_value)

def Model(
    __extends__: Type[Json] | List[Type[Json]] = None,
    __conditions__=None,
    __exact__=False,
    __ordered__=False,
    __rigid__=False,
    **kwargs: Type
) -> Type[Json]:
    if __rigid__:
        __exact__ = True
        __ordered__ = True
    if __exact__ and __ordered__:
        return Rigid(__extends__=__extends__, __conditions__=__conditions__, **kwargs)
    elif __exact__:
        return Exact(__extends__=__extends__, __conditions__=__conditions__, **kwargs)
    elif __ordered__:
        return Ordered(__extends__=__extends__, __conditions__=__conditions__, **kwargs)

    extended_models = _process_extends(__extends__)
    if extended_models:
        kwargs = _merge_attrs(extended_models, kwargs)
    if not kwargs:
        return dict

    if not all(isinstance(key, str) for key in kwargs.keys()):
        raise TypeError("All arguments to Model must be strings representing attribute names.")
    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _collect_attributes(kwargs)
    conditions = []
    if __conditions__:
        conditions = list(__conditions__) if isinstance(__conditions__, (list, tuple)) else [__conditions__]

    class ModelInstance(dict):
        _defined_required_attributes: dict = {}
        _defined_optional_attributes: dict = {}
        _defined_keys: set = set()
        _ordered_keys: list = _get_keys_in_defined_order(attributes_and_types, optional_attributes_and_defaults)

        def __init__(self, *args, **data):
            super().__init__()
            for key, wrapper in self.__class__._defined_optional_attributes.items():
                super().__setitem__(key, wrapper.default_value)
            for key, value in data.items():
                self.__setattr__(key, value)
            for req_key in self.__class__._defined_required_attributes.keys():
                if req_key not in self:
                    raise TypeError(
                        f"Missing required attribute '{req_key}' during {self.__class__.__name__} initialization."
                    )

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

    class _Model(_ModelFactory):
        def __new__(cls, name, bases, dct):
            new_type = super().__new__(cls, name, bases, dct)
            setattr(new_type, '_defined_required_attributes', dict(dct.get('_initial_attributes_and_types', ())))
            setattr(new_type, '_defined_optional_attributes', dct.get('_initial_optional_attributes_and_defaults', {}))
            setattr(new_type, '_defined_keys',
                    set(dict(dct.get('_initial_attributes_and_types', ())).keys()) |
                    set(dct.get('_initial_optional_attributes_and_defaults', {}).keys()))
            setattr(new_type, '_required_attributes_and_types', dct.get('_initial_attributes_and_types', ()))
            setattr(new_type, '_required_attribute_keys', dct.get('_initial_required_attribute_keys', set()))
            setattr(new_type, '_optional_attributes_and_defaults', dct.get('_initial_optional_attributes_and_defaults', {}))
            setattr(new_type, '__conditions_list', dct.get('_initial_conditions', []))
            setattr(new_type, '_ordered_keys', dct.get('_initial_ordered_keys', []))
            return new_type

        def __init__(cls, name, bases, dct):
            for key in ['_initial_attributes_and_types', '_initial_required_attribute_keys',
                        '_initial_optional_attributes_and_defaults', '_initial_conditions', '_initial_ordered_keys']:
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
            for cond in getattr(cls, '__conditions_list', []):
                if not cond(instance):
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
            parent_conds = set(getattr(cls, '__conditions_list', []))
            child_conds = set(getattr(subclass, '__conditions_list', []))
            if not parent_conds.issubset(child_conds):
                return False
            return True

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, _Optional) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    ordered_keys = _get_keys_in_defined_order(attributes_and_types, optional_attributes_and_defaults)
    class_name = f"Model({args_str})"
    return _Model(
        class_name,
        (ModelInstance, ModelFactory),
        {
            '_initial_attributes_and_types': attributes_and_types,
            '_initial_required_attribute_keys': required_attribute_keys,
            '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults,
            '_initial_conditions': conditions,
            '_initial_ordered_keys': ordered_keys
        }
    )

def Exact(
    __extends__: Type[Json] | List[Type[Json]] = None,
    __conditions__=None,
    **kwargs: Type
) -> Type[Json]:

    extended_models = _process_extends(__extends__)
    if extended_models:
        kwargs = _merge_attrs(extended_models, kwargs)

    if not kwargs:
        return dict

    if not all(isinstance(key, str) for key in kwargs.keys()):
        raise TypeError("All arguments to Exact must be strings representing attribute names.")
    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _collect_attributes(kwargs)

    all_possible_keys = required_attribute_keys | set(optional_attributes_and_defaults.keys())
    conditions = []
    if __conditions__:
        conditions = list(__conditions__) if isinstance(__conditions__, (list, tuple)) else [__conditions__]

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

    class _Exact(_ModelFactory):
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
            setattr(new_type, '__conditions_list', dct.get('_initial_conditions', []))
            return new_type

        def __init__(cls, name, bases, dct):
            for key in ['_initial_attributes_and_types', '_initial_required_attribute_keys',
                        '_initial_optional_attributes_and_defaults', '_initial_all_possible_keys', '_initial_conditions']:
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

            for cond in getattr(cls, '__conditions_list', []):
                if not cond(instance):
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
            parent_conds = set(getattr(cls, '__conditions_list', []))
            child_conds = set(getattr(subclass, '__conditions_list', []))
            if not parent_conds.issubset(child_conds):
                return False
            return True
    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, _Optional) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    class_name = f"Exact({args_str})"
    return _Exact(
        class_name,
        (ExactInstance, ModelFactory),
        {
            '_initial_attributes_and_types': attributes_and_types,
            '_initial_required_attribute_keys': required_attribute_keys,
            '_initial_optional_attributes_and_defaults': optional_attributes_and_defaults,
            '_initial_all_possible_keys': all_possible_keys,
            '_initial_conditions': conditions,
        }
    )

def Ordered(
    __extends__: Type[Json] | List[Type[Json]] = None,
    __conditions__=None,
    **kwargs: Type
) -> Type[Json]:
    extended_models = _process_extends(__extends__)
    if extended_models:
        kwargs = _merge_attrs(extended_models, kwargs)
    if not kwargs:
        return dict
    if not all(isinstance(key, str) for key in kwargs.keys()):
        raise TypeError("All arguments to Ordered must be strings representing attribute names.")
    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _collect_attributes(kwargs)
    ordered_keys = _get_keys_in_defined_order(attributes_and_types, optional_attributes_and_defaults)
    conditions = []
    if __conditions__:
        conditions = list(__conditions__) if isinstance(__conditions__, (list, tuple)) else [__conditions__]

    class OrderedInstance(dict):
        _ordered_keys: list = ordered_keys
        _defined_required_attributes = dict(attributes_and_types)
        _defined_optional_attributes = optional_attributes_and_defaults
        _defined_keys = set(_ordered_keys)

        def __init__(self, *args, **data):
            super().__init__()
            if list(data.keys()) != self._ordered_keys:
                raise TypeError(
                    f"Input keys order {list(data.keys())} does not match order in model: {self._ordered_keys}"
                )
            for key, wrapper in self._defined_optional_attributes.items():
                super().__setitem__(key, wrapper.default_value)
            for key, value in data.items():
                self.__setattr__(key, value)
            for req_key in self._defined_required_attributes.keys():
                if req_key not in self:
                    raise TypeError(
                        f"Missing required attribute '{req_key}' during {self.__class__.__name__} initialization."
                    )

        def __getattr__(self, name):
            if name in self._defined_keys:
                if name in self:
                    return self[name]
                elif name in self._defined_optional_attributes:
                    return self._defined_optional_attributes[name].default_value
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"{self.__class__.__name__} has no attribute {name}")

        def __setattr__(self, name, value):
            if name in self._defined_required_attributes:
                expected_type = self._defined_required_attributes[name]
                if not (isinstance(value, expected_type) or
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(f"{name} type mismatch: {type(value)} vs {expected_type}")
                self[name] = value
            elif name in self._defined_optional_attributes:
                expected_type = self._defined_optional_attributes[name].type
                if not (isinstance(value, expected_type) or
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(f"{name} type mismatch: {type(value)} vs {expected_type}")
                self[name] = value
            else:
                object.__setattr__(self, name, value)

    class _Ordered(_ModelFactory):
        def __new__(cls, name, bases, dct):
            new_type = super().__new__(cls, name, bases, dct)
            setattr(new_type, '_ordered_keys', dct.get('_initial_ordered_keys'))
            setattr(new_type, '__conditions_list', dct.get('_initial_conditions', []))
            return new_type

        def __instancecheck__(cls, instance):
            if not isinstance(instance, dict):
                return False
            instance_keys = list(instance.keys())
            model_keys = getattr(cls, '_ordered_keys', [])
            if instance_keys != model_keys[:len(instance_keys)]:
                return False
            i = 0
            for k in model_keys:
                if k in instance:
                    if i >= len(instance_keys) or instance_keys[i] != k:
                        return False
                    v = instance[k]
                    if k in cls._defined_required_attributes:
                        typ = cls._defined_required_attributes[k]
                    else:
                        typ = cls._defined_optional_attributes[k].type
                    if not (isinstance(v, typ) or (hasattr(typ, '__instancecheck__') and typ.__instancecheck__(v))):
                        return False
                    i += 1
            for cond in getattr(cls, '__conditions_list', []):
                if not cond(instance):
                    return False
            return True

        def __subclasscheck__(cls, subclass):
            if not hasattr(subclass, '_ordered_keys'):
                return False
            return list(getattr(cls, '_ordered_keys')) == list(getattr(subclass, '_ordered_keys'))

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, _Optional) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    class_name = f"Ordered({args_str})"
    return _Ordered(
        class_name,
        (OrderedInstance, ModelFactory),
        {
            '_initial_ordered_keys': ordered_keys,
            '_initial_conditions': conditions,
        }
    )

def Rigid(
    __extends__: Type[Json] | List[Type[Json]] = None,
    __conditions__=None,
    **kwargs: Type
) -> Type[Json]:
    extended_models = _process_extends(__extends__)
    if extended_models:
        kwargs = _merge_attrs(extended_models, kwargs)
    if not kwargs:
        return dict
    if not all(isinstance(key, str) for key in kwargs.keys()):
        raise TypeError("All arguments to Rigid must be strings representing attribute names.")
    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _collect_attributes(kwargs)
    ordered_keys = _get_keys_in_defined_order(attributes_and_types, optional_attributes_and_defaults)
    all_possible_keys = required_attribute_keys | set(optional_attributes_and_defaults.keys())
    conditions = []
    if __conditions__:
        conditions = list(__conditions__) if isinstance(__conditions__, (list, tuple)) else [__conditions__]

    class RigidInstance(dict):
        _ordered_keys: list = ordered_keys
        _required_attribute_keys = required_attribute_keys
        _defined_required_attributes = dict(attributes_and_types)
        _defined_optional_attributes = optional_attributes_and_defaults
        _defined_keys = set(_ordered_keys)

        def __init__(self, **data):
            super().__init__()
            if list(data.keys()) != self._ordered_keys:
                raise TypeError(
                    f"Input keys order {list(data.keys())} does not match order in model: {self._ordered_keys}"
                )
            for key in self._ordered_keys:
                if key in data:
                    self[key] = data[key]
                elif key in self._defined_optional_attributes:
                    self[key] = self._defined_optional_attributes[key].default_value
            for req_key in self._defined_required_attributes:
                if req_key not in self:
                    raise TypeError(
                        f"Missing required attribute '{req_key}' during {self.__class__.__name__} initialization."
                    )

    class _Rigid(_ModelFactory):
        def __new__(cls, name, bases, dct):
            new_type = super().__new__(cls, name, bases, dct)
            setattr(new_type, '_ordered_keys', dct.get('_initial_ordered_keys'))
            setattr(new_type, '_required_attribute_keys', dct.get('_initial_required_attribute_keys', set()))
            setattr(new_type, '_defined_required_attributes', dict(attributes_and_types))
            setattr(new_type, '_defined_optional_attributes', optional_attributes_and_defaults)
            setattr(new_type, '__conditions_list', dct.get('_initial_conditions', []))
            setattr(new_type, '_all_possible_keys', set(required_attribute_keys | set(optional_attributes_and_defaults.keys())))
            return new_type

        def __instancecheck__(cls, instance):
            if not isinstance(instance, dict):
                return False
            instance_keys = list(instance.keys())
            model_keys = getattr(cls, '_ordered_keys', [])
            if instance_keys != model_keys:
                return False
            exp_keys = set(model_keys)
            if set(instance_keys) != exp_keys:
                return False
            for k in model_keys:
                v = instance[k]
                if k in cls._defined_required_attributes:
                    typ = cls._defined_required_attributes[k]
                else:
                    typ = cls._defined_optional_attributes[k].type
                if not (isinstance(v, typ) or (hasattr(typ, '__instancecheck__') and typ.__instancecheck__(v))):
                    return False
            for cond in getattr(cls, '__conditions_list', []):
                if not cond(instance):
                    return False
            return True

        def __subclasscheck__(cls, subclass):
            return (
                hasattr(subclass, '_ordered_keys')
                and list(getattr(cls, '_ordered_keys')) == list(getattr(subclass, '_ordered_keys'))
            )

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, _Optional) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    class_name = f"Rigid({args_str})"
    return _Rigid(
        class_name,
        (RigidInstance, ModelFactory),
        {
            '_initial_required_attribute_keys': required_attribute_keys,
            '_initial_ordered_keys': ordered_keys,
            '_initial_conditions': conditions,
        }
    )

def Instance(entity: dict, model: Type[Json]) -> Json:
    model_metaclass = type(model)

    if not isinstance(model, MODEL_METATYPES):
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
                    f" ==> '{attr_name}': has a wrong type.\n" +
                    f"     [received_type]: '{_get_type_display_name(type(actual_value))}'\n" +
                    f"     [expected_type]: '{_get_type_display_name(expected_type)}'"
                )
    if model_metaclass.__name__ == "_Exact":
        all_expected_keys = required_attribute_keys | set(optional_attributes_and_defaults.keys())
        extra_keys = set(entity.keys()) - all_expected_keys
        if extra_keys:
            errors.append(f"\t ==> Extra attributes found: {', '.join(sorted(extra_keys))}.")
    if model_metaclass.__name__ == "_Conditional":
        conds = getattr(model, '__conditions_list', [])
        if not conds and hasattr(model, '__bases__') and model.__bases__ and issubclass(model.__bases__[0], Json):
            pass
    conds = getattr(model, '__conditions_list', [])
    for cond in conds:
        if not cond(entity):
            errors.append(f" ==> Condition {getattr(cond, '__name__', cond)} failed for {entity}")

    if errors:
        raise TypeError(
            f"'{repr(entity)}' is not an instance of model '{_get_type_display_name(model)}':\n"
            + "\n".join(errors)
        )
    return entity

def Forget(model: Type[Json], entries: list) -> Type[Json]:
    if not isinstance(model, type(_MODEL)):
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

def model(_cls=None, *, extends=None, conditions=None, exact=False, ordered=False, rigid=False):
    def wrap(cls):
        annotations = cls.__annotations__
        kwargs = {name: type_hint for name, type_hint in annotations.items()}
        return_model = Model(
            __extends__=extends,
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
    if _cls is None: return wrap
    else: return wrap(_cls)

def exact(_cls=None, *, extends=None, conditions=None):
    def wrap(cls):
        annotations = cls.__annotations__
        kwargs = {name: type_hint for name, type_hint in annotations.items()}
        exact_model = Exact(__extends__=extends, __conditions__=conditions, **kwargs)
        exact_model.__name__ = cls.__name__
        exact_model.__qualname__ = cls.__qualname__
        exact_model.__module__ = cls.__module__
        exact_model.__doc__ = cls.__doc__
        return exact_model
    if _cls is None: return wrap
    else: return wrap(_cls)

def ordered(_cls=None, *, extends=None, conditions=None):
    def wrap(cls):
        annotations = cls.__annotations__
        kwargs = {name: type_hint for name, type_hint in annotations.items()}
        res = Ordered(__extends__=extends, __conditions__=conditions, **kwargs)
        res.__name__ = cls.__name__
        res.__qualname__ = cls.__qualname__
        res.__module__ = cls.__module__
        res.__doc__ = cls.__doc__
        return res
    if _cls is None: return wrap
    else: return wrap(_cls)

def rigid(_cls=None, *, extends=None, conditions=None):
    def wrap(cls):
        annotations = cls.__annotations__
        kwargs = {name: type_hint for name, type_hint in annotations.items()}
        res = Rigid(__extends__=extends, __conditions__=conditions, **kwargs)
        res.__name__ = cls.__name__
        res.__qualname__ = cls.__qualname__
        res.__module__ = cls.__module__
        res.__doc__ = cls.__doc__
        return res
    if _cls is None: return wrap
    else: return wrap(_cls)
