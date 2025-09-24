from typed.mods.meta.base import DICT
from typed.mods.types.base import TYPE, Str, Dict, List, Tuple, Bool
from typed.mods.factories.base import Union
from typed.mods.factories.generics import Maybe
from typed.mods.helper.helper import _name
from typed.mods.meta.models import (
    _MODEL_INSTANCE_,
    _MODEL_FACTORY_,
    _MODEL_,
    _EXACT_,
    _ORDERED_,
    _RIGID_,
    _OPTIONAL_,
    _MANDATORY_
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
    if not isinstance(typ, type) and not hasattr(typ, '__instancecheck__'):
        raise TypeError(f"'{_name(typ)}' is not a type.")
    from typed.mods.types.base import Any
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
    elif __exact__:
        return Exact(__extends__=__extends__, __conditions__=__conditions__, **kwargs)
    elif __ordered__:
        return Ordered(__extends__=__extends__, __conditions__=__conditions__, **kwargs)

    extended_models = _process_extends(__extends__)
    if extended_models:
        kwargs = _merge_attrs(extended_models, kwargs)
    if not kwargs:
        return dict

    for key in kwargs.keys():
        if not key in Str:
            raise TypeError(
                "Wrong type while creating model:\n"
                f" ==> '{_name(key)}': has unexpected type\n"
                 "     [expected_type] subtype of 'Str'\n"
                f"     [received_type] '{_name(TYPE(key))}'"
            )

    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _attrs(kwargs)
    conditions = []
    if __conditions__:
        conditions = list(__conditions__) if isinstance(__conditions__, (List, Tuple)) else [__conditions__]

    class MODEL_INSTANCE(Dict, metaclass=_MODEL_INSTANCE_):
        _defined_required_attributes = {}
        _defined_optional_attributes = {}
        _defined_keys: set = set()
        _ordered_keys: list = _ordered_keys(attributes_and_types, optional_attributes_and_defaults)

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

        def __getattr__(self, name):
            if name in self._defined_keys:
                if name in self:
                    return self[name]
                elif name in self._defined_optional_attributes:
                    return self._defined_optional_attributes[name].default_value
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        def __setattr__(self, name, value):
            if name in self._defined_required_attributes:
                expected_type = self._defined_required_attributes[name]
                if not (isinstance(value, expected_type) or
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(
                        f"Attempted to set '{name}' to value '{value}' with type '{_name(type(value))}', "
                        f"but expected type '{_name(expected_type)}'."
                    )
                self[name] = value
            elif name in self._defined_optional_attributes:
                expected_type = self._defined_optional_attributes[name].type
                if not (isinstance(value, expected_type) or
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(
                        f"Attempted to set '{name}' to value '{value}' with type '{_name(type(value))}', "
                        f"but expected type '{_name(expected_type)}'."
                    )
                self[name] = value
            else:
                object.__setattr__(self, name, value)

        def __delattr__(self, name):
            if name in self._defined_required_attributes:
                raise AttributeError(f"Cannot delete required attribute '{name}' from a '{self.__class__.__name__}' object.")
            elif name in self._defined_optional_attributes:
                if name in self:
                    del self[name]
                else:
                    raise AttributeError(f"'{name}' not found in '{self.__class__.__name__}' object.")
            else:
                object.__delattr__(self, name)

    class _MODEL(_MODEL_FACTORY_, _MODEL_, _MODEL_INSTANCE_):
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

        def __instancecheck__(cls, instance):
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

        def __subclasscheck__(cls, subclass):
            if not hasattr(subclass, '_required_attributes_and_types') or \
               not hasattr(subclass, '_required_attribute_keys') or \
               not hasattr(subclass, '_optional_attributes_and_defaults'):
                return False
            if not isinstance(subclass, TYPE):
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
                    if not (isinstance(subclass_type, TYPE) and issubclass(subclass_type, parent_type)) and \
                       not (hasattr(parent_type, '__subclasscheck__') and parent_type.__subclasscheck__(subclass_type)):
                        return False
                elif attr_name in subclass_optional_attrs_defaults:
                    return False
            for attr_name, parent_wrapper in cls_optional_attrs_defaults.items():
                parent_type = parent_wrapper.type
                if attr_name in subclass_required_attrs:
                    subclass_type = subclass_required_attrs[attr_name]
                    if not (isinstance(subclass_type, TYPE) and issubclass(subclass_type, parent_type)) and \
                       not (hasattr(parent_type, '__subclasscheck__') and parent_type.__subclasscheck__(subclass_type)):
                        return False
                elif attr_name in subclass_optional_attrs_defaults:
                    subclass_wrapper = subclass_optional_attrs_defaults[attr_name]
                    subclass_type = subclass_wrapper.type
                    subclass_default_value = subclass_wrapper.default_value
                    if not (isinstance(subclass_type, TYPE) and issubclass(subclass_type, parent_type)) and \
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

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, OPTIONAL) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    ordered_keys = _ordered_keys(attributes_and_types, optional_attributes_and_defaults)
    class_name = f"Model({args_str})"

    new_model = _MODEL(
        class_name,
        (MODEL_INSTANCE, MODEL_FACTORY, MODEL),
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
        if not key in Str:
            raise TypeError(
                "Wrong type while creating model:\n"
                f" ==> '{_name(key)}': has unexpected type\n"
                 "     [expected_type] subtype of 'Str'\n"
                f"     [received_type] '{_name(TYPE(key))}'"
            )
    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _attrs(kwargs)

    all_possible_keys = required_attribute_keys | set(optional_attributes_and_defaults.keys())
    conditions = []
    if __conditions__:
        conditions = list(__conditions__) if isinstance(__conditions__, (List, Tuple)) else [__conditions__]

    class EXACT_INSTANCE(Dict, metaclass=_MODEL_INSTANCE_):
        _defined_required_attributes = {}
        _defined_optional_attributes = {}
        _defined_keys = set()
        _all_possible_keys = set()

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

        def __setattr__(self, name, value):
            if name in self._defined_required_attributes:
                expected_type = self._defined_required_attributes[name]
                if not (value in expected_type) or (
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(
                        f"Attempted to set '{name}' to value '{value}' with type '{_name(type(value))}', "
                        f"but expected type '{_name(expected_type)}'."
                    )
                self[name] = value
            elif name in self._defined_optional_attributes:
                expected_type = self._defined_optional_attributes[name].type
                if not (value in expected_type) or (
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(
                        f"Attempted to set '{name}' to value '{value}' with type '{_name(type(value))}', "
                        f"but expected type '{_name(expected_type)}'."
                    )
                self[name] = value
            else:
                object.__setattr__(self, name, value)

        def __delattr__(self, name):
            if name in self._defined_required_attributes:
                raise AttributeError(f"Cannot delete required attribute '{name}' from a '{self.__class__.__name__}' object.")
            elif name in self._defined_optional_attributes:
                if name in self:
                    del self[name]
                else:
                    raise AttributeError(f"'{name}' not found in '{self.__class__.__name__}' object.")
            else:
                object.__delattr__(self, name)

    class _EXACT(_MODEL_FACTORY_, _EXACT_, _MODEL_INSTANCE_):
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

        def __instancecheck__(cls, instance):
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

                if not (subclass_type in TYPE) and _issubtype(subclass_type, parent_type) and \
                   not (hasattr(parent_type, '__subclasscheck__') and parent_type.__subclasscheck__(subclass_type)):
                    return False

                if not (subclass_default_value in parent_type) or (
                        (hasattr(parent_type, '__instancecheck__') and parent_type.__instancecheck__(subclass_default_value))):
                    return False

            for attr_name in cls_required_keys:
                parent_type = cls_required_attrs[attr_name]
                if attr_name not in subclass_required_attrs:
                    return False

                subclass_type = subclass_required_attrs[attr_name]

                if not (subclass_type in TYPE) and _issubtype(subclass_type, parent_type) and \
                   not (hasattr(parent_type, '__subclasscheck__') and parent_type.__subclasscheck__(subclass_type)):
                    return False
            parent_conds = set(getattr(cls, '__conditions_list', []))
            child_conds = set(getattr(subclass, '__conditions_list', []))
            if not parent_conds.issubset(child_conds):
                return False
            return True

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, OPTIONAL) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    class_name = f"Exact({args_str})"

    new_model = _EXACT(
        class_name,
        (EXACT_INSTANCE, MODEL_FACTORY, EXACT),
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
        if not key in Str:
            raise TypeError(
                "Wrong type while creating model:\n"
                f" ==> '{_name(key)}': has unexpected type\n"
                 "     [expected_type] subtype of 'Str'\n"
                f"     [received_type] '{_name(TYPE(key))}'"
            )

    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _attrs(kwargs)
    ordered_keys = _ordered_keys(attributes_and_types, optional_attributes_and_defaults)
    conditions = []
    if __conditions__:
        conditions = list(__conditions__) if isinstance(__conditions__, (List, Tuple)) else [__conditions__]

    class ORDERED_INSTANCE(Dict, metaclass=_MODEL_INSTANCE_):
        _ordered_keys = ordered_keys
        _defined_required_attributes = dict(attributes_and_types)
        _defined_optional_attributes = optional_attributes_and_defaults
        _defined_keys = set(_ordered_keys)

        def __init__(self, **data):
            super().__init__()
            print(data)
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
                if not (value in expected_type) or (
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(f"{name} type mismatch: {TYPE(value)} vs {expected_type}")
                self[name] = value
            elif name in self._defined_optional_attributes:
                expected_type = self._defined_optional_attributes[name].type
                if not (value in expected_type) or (
                        (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                    raise TypeError(f"{name} type mismatch: {TYPE(value)} vs {expected_type}")
                self[name] = value
            else:
                object.__setattr__(self, name, value)

    class _ORDERED(_MODEL_FACTORY_, _MODEL_INSTANCE_, _ORDERED_):
        def __new__(cls, name, bases, dct):
            new_type = super().__new__(cls, name, bases, dct)
            setattr(new_type, '_ordered_keys', dct.get('_initial_ordered_keys'))
            setattr(new_type, '__conditions_list', dct.get('_initial_conditions', []))
            return new_type

        def __instancecheck__(cls, instance):
            if not instance in Dict:
                print("aaaaa")
                return False
            instance_keys = list(instance.keys())
            model_keys = getattr(cls, '_ordered_keys', [])
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
                    if not (v in typ) or (hasattr(typ, '__instancecheck__') and not typ.__instancecheck__(v)):
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

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not isinstance(value, OPTIONAL) else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    class_name = f"Ordered({args_str})"

    new_model = _ORDERED(
        class_name,
        (ORDERED_INSTANCE, MODEL_FACTORY, ORDERED),
        {
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
    if not kwargs:
        return dict

    for key in kwargs.keys():
        if not key in Str:
            raise TypeError(
                "Wrong type while creating model:\n"
                f" ==> '{_name(key)}': has unexpected type\n"
                 "     [expected_type] subtype of 'Str'\n"
                f"     [received_type] '{_name(TYPE(key))}'"
            )

    attributes_and_types, required_attribute_keys, optional_attributes_and_defaults = _attrs(kwargs)
    ordered_keys = _ordered_keys(attributes_and_types, optional_attributes_and_defaults)
    all_possible_keys = required_attribute_keys | set(optional_attributes_and_defaults.keys())
    conditions = []
    if __conditions__:
        conditions = list(__conditions__) if isinstance(__conditions__, (list, tuple)) else [__conditions__]

    class RIGID_INSTANCE(Dict, metaclass=_MODEL_INSTANCE_):
        _ordered_keys = ordered_keys
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

    class _RIGID(_MODEL_FACTORY_, _MODEL_INSTANCE_, _RIGID_):
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
            if not instance in Dict:
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
                if not (v in typ) or (hasattr(typ, '__instancecheck__') and typ.__instancecheck__(v)):
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

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" if not value in OPTIONAL else f"{key}: {getattr(value.type, '__name__', str(value.type))} = {repr(value.default_value)}" for key, value in kwargs.items())
    class_name = f"Rigid({args_str})"

    new_model = _RIGID(
        class_name,
        (RIGID_INSTANCE, MODEL_FACTORY, RIGID),
        {
            '_initial_required_attribute_keys': required_attribute_keys,
            '_initial_ordered_keys': ordered_keys,
            '_initial_conditions': conditions,
        }
    )

    _attach_model_attrs(new_model, extended_models)
    new_model.is_rigid = True
    from typed.mods.helper.null import _null_model
    new_model.__null__ = _null_model(new_model)
    new_model.__display___ = class_name
    return new_model

@typed
def Validate(entity: Dict, model: MODEL) -> Dict:
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
            raise TypeError(f"{repr(entity)} is not a {model_name}:\n" + "\n".join(errors))
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
            raise TypeError(f"{repr(entity)} is not a {model_name}:\n" + "\n".join(errors))
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
            raise TypeError(f"{repr(entity)} is not a {model_name}:\n" + "\n".join(errors))
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
        raise TypeError(f"{repr(entity)} is not a {model_name}:\n" + "\n".join(errors))
    return entity

def Forget(model, entries):
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

def model(_cls=None, *, extends=None, conditions=None, exact=False, ordered=False, rigid=False, nullable=False):
    def wrap(cls):
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
    if _cls is None:
        return wrap
    else:
        return wrap(_cls)

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

def optional(_cls=None, *, extends=None, conditions=None, exact=False, ordered=False, rigid=False, nullable=False):
    def wrap(cls):
        is_null = getattr(cls, '__nullable__', nullable)

        if getattr(cls, 'is_model', False):
            old_req = getattr(cls, '_required_attributes_and_types', ())
            old_opt = getattr(cls, '_optional_attributes_and_defaults', {})

            new_kwargs = {}
            for name, typ in old_req:
                new_kwargs[name] = _optional(typ, None, is_null)
            for name, wrappr in old_opt.items():
                new_kwargs[name] = _optional(wrappr.type, wrappr.default_value, is_null)

            if getattr(cls, 'is_exact', False):
                new_m = Exact(__extends__=cls, **new_kwargs)
            elif getattr(cls, 'is_rigid', False):
                new_m = Rigid(__extends__=cls, **new_kwargs)
            elif getattr(cls, 'is_ordered', False):
                new_m = Ordered(__extends__=cls, **new_kwargs)
            else:
                new_m = Model(__extends__=cls, **new_kwargs)

            new_m.is_optional  = True
            new_m.is_mandatory = False

            for a in ('__name__','__qualname__','__module__','__doc__'):
                setattr(new_m, a, getattr(cls, a))
            return new_m

        ann = getattr(cls, '__annotations__', {})
        kwargs = {}
        for name, hint in ann.items():
            default = getattr(cls, name, None)
            kwargs[name] = _optional(hint, default, is_null)

        built = Model(
            __extends__   = extends,
            __conditions__= conditions,
            __exact__     = exact,
            __ordered__   = ordered,
            __rigid__     = rigid,
            **kwargs
        )
        for a in ('__name__','__qualname__','__module__','__doc__'):
            setattr(built, a, getattr(cls, a))
        return built

    if _cls is None:
        return wrap
    else:
        return wrap(_cls)

def mandatory(_cls=None, *, extends=None, conditions=None, exact=False, ordered=False, rigid=False):
    def wrap(cls):
        if getattr(cls, 'is_model', False):
            old_req = getattr(cls, '_required_attributes_and_types', ())
            old_opt = getattr(cls, '_optional_attributes_and_defaults', {})

            new_kwargs = {}
            for name, typ in old_req:
                new_kwargs[name] = typ
            for name, wrappr in old_opt.items():
                new_kwargs[name] = wrappr.type

            if getattr(cls, 'is_exact', False):
                new_m = Exact(__extends__=cls, **new_kwargs)
            elif getattr(cls, 'is_rigid', False):
                new_m = Rigid(__extends__=cls, **new_kwargs)
            elif getattr(cls, 'is_ordered', False):
                new_m = Ordered(__extends__=cls, **new_kwargs)
            else:
                new_m = Model(__extends__=cls, **new_kwargs)

            new_m.is_mandatory = True
            new_m.is_optional  = False

            for a in ('__name__','__qualname__','__module__','__doc__'):
                setattr(new_m, a, getattr(cls, a))
            return new_m

        ann = getattr(cls, '__annotations__', {})
        kwargs = {}
        for name, hint in ann.items():
            if isinstance(hint, _Optional):
                base = hint.type
            else:
                base = hint
            kwargs[name] = base

        built = Model(
            __extends__   = extends,
            __conditions__= conditions,
            __exact__     = exact,
            __ordered__   = ordered,
            __rigid__     = rigid,
            **kwargs
        )
        for a in ('__name__','__qualname__','__module__','__doc__'):
            setattr(built, a, getattr(cls, a))
        built.is_mandatory = True
        built.is_optional  = False
        return built

    if _cls is None:
        return wrap
    else:
        return wrap(_cls)
