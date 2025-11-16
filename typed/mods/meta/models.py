from typed.mods.meta.base import _TYPE_, DICT
from typed.mods.meta.func import FACTORY
from typed.mods.types.base import TYPE, Set, Dict
from typed.mods.helper.helper import _issubtype, _name

def _single_field_inner_type_and_key(mcls):
    """
    If mcls is a model with exactly one required attribute and no optional ones,
    return (inner_type, key_name). Otherwise return (None, None).
    """
    try:
        req_tuple = getattr(mcls, '_required_attributes_and_types', ())
        req = dict(req_tuple)
        opt = getattr(mcls, '_optional_attributes_and_defaults', {})
        if len(req) == 1 and len(opt) == 0:
            key, inner_type = next(iter(req.items()))
            return inner_type, key
    except Exception:
        pass
    return None, None

class _MODEL_INSTANCE_(DICT):
    def __instancecheck__(cls, instance):
        if not instance in Dict:
            return False

class _MODEL_FACTORY_(FACTORY):
    def __getattr__(cls, name):
        try:
            req_attrs = object.__getattribute__(cls, '_defined_required_attributes')
            if name in req_attrs:
                return req_attrs[name]

            opt_attrs = object.__getattribute__(cls, '_defined_optional_attributes')
            if name in opt_attrs:
                return opt_attrs[name].type
        except AttributeError:
            pass

        raise AttributeError(f"Model '{_name(cls)}' has no attribute '{_name(name)}'.")

    def __setattr__(cls, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
            return

        from typed.mods.helper.models import _update_model_attr, _Optional
        from typed.mods.types.base import TYPE

        is_type_like = isinstance(value, (TYPE, _Optional)) or \
                       (hasattr(value, '__instancecheck__') and callable(value.__instancecheck__))

        if is_type_like:
            _update_model_attr(cls, name, value)
        else:
            is_model_field = False
            try:
                req_attrs = object.__getattribute__(cls, '_defined_required_attributes')
                opt_attrs = object.__getattribute__(cls, '_defined_optional_attributes')
                if name in req_attrs or name in opt_attrs:
                    is_model_field = True
            except AttributeError:
                pass

            if is_model_field:
                raise TypeError(
                    "Wrong type while setting model attribute:\n"
                    f" ==> '{_name(name)}': has value of an unexpected type\n"
                    f"     [received_value] '{value}'\n"
                     "     [expected_type] subtype of TYPE\n"
                    f"     [received_type] {_name(TYPE(value))}"
                )
            else:
                super().__setattr__(name, value)

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
            if not isinstance(entity, Dict):
                raise TypeError(f"Expected a dictionary or keyword arguments, got {type(entity)}")
            entity_dict = entity.copy()
        else:
            entity_dict = kwargs
        optional_defaults = getattr(cls, '_optional_attributes_and_defaults', {})
        for attr, wrapper in optional_defaults.items():
            if attr not in entity_dict:
                entity_dict[attr] = wrapper.default_value

        if not cls.__instancecheck__(entity_dict):
            from typed.mods.models import validate
            validate(entity_dict, cls)
        obj = cls.__new__(cls)
        obj.__init__(**entity_dict)
        return obj

class _MODEL_(_TYPE_):
    def __instancecheck__(cls, instance):
        return getattr(instance, 'is_model', False)

class _EXACT_(_MODEL_):
    def __instancecheck__(cls, instance):
        return getattr(instance, 'is_exact', False)

class _ORDERED_(_MODEL_):
    def __instancecheck__(cls, instance):
        return getattr(instance, 'is_ordered', False)

class _RIGID_(_EXACT_, _ORDERED_):
    def __instancecheck__(cls, instance):
        return getattr(instance, 'is_rigid', False)

class _OPTIONAL_(_MODEL_):
    def __instancecheck__(cls, instance):
        if instance in TYPE:
            mcls = instance
        else:
            mcls = instance.__class__
        if not getattr(mcls, 'is_model', False):
            return False
        req = getattr(mcls, '_required_attribute_keys', None)
        return isinstance(req, Set) and len(req) == 0

    def __subclasscheck__(cls, subclass):
        if not _issubtype(subclass, TYPE):
            return False
        if not getattr(subclass, 'is_model', False):
            return False
        req = getattr(subclass, '_required_attribute_keys', None)
        return isinstance(req, Set) and len(req) == 0

class _MANDATORY_(_MODEL_):
    def __instancecheck__(cls, instance):
        if instance in TYPE:
            mcls = instance
        else:
            mcls = instance.__class__
        if not getattr(mcls, 'is_model', False):
            return False
        opts = getattr(mcls, '_optional_attributes_and_defaults', None)
        return isinstance(opts, Dict) and len(opts) == 0

    def __subclasscheck__(cls, subclass):
        if not _issubtype(cls, TYPE):
            return False
        if not getattr(subclass, 'is_model', False):
            return False
        opts = getattr(subclass, '_optional_attributes_and_defaults', None)
        return isinstance(opts, Dict) and len(opts) == 0

class MODEL_INSTANCE(Dict, metaclass=_MODEL_INSTANCE_):
    _defined_required_attributes = {}
    _defined_optional_attributes = {}
    _defined_keys: set = set()
    _ordered_keys: list = []

    def __init__(self, **data):
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
            raise AttributeError(f"'{_name(self.__class__)}' object has no attribute '{name}'")


    def __setattr__(self, name, value):
        if name in self._defined_required_attributes:
            expected_type = self._defined_required_attributes[name]
            if not (isinstance(value, expected_type) or
                    (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                raise TypeError(
                    f"Attempted to set '{name}' to value '{value}' with type '{_name(TYPE(value))}', "
                    f"but expected type '{_name(expected_type)}'."
                )
            self[name] = value
        elif name in self._defined_optional_attributes:
            expected_type = self._defined_optional_attributes[name].type
            if not (isinstance(value, expected_type) or
                    (hasattr(expected_type, '__instancecheck__') and expected_type.__instancecheck__(value))):
                raise TypeError(
                    f"Attempted to set '{name}' to value '{value}' with type '{_name(TYPE(value))}', "
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
                raise AttributeError(f"'{name}' not found in '{_name(self.__class__)}' object.")
        else:
            object.__delattr__(self, name)

    @property
    def __json__(self):
        from typed.mods.helper.models import _to_json
        return _to_json(self)

class MODEL_META(_MODEL_FACTORY_, _MODEL_, _MODEL_INSTANCE_):
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
        if hasattr(instance, '__class__') and cls in getattr(
            instance, '__mro__', getattr(instance.__class__, '__mro__', [])
        ):
            return True

        if not (instance in Dict):
            inner_type, key_name = _single_field_inner_type_and_key(cls)
            if inner_type is not None:
                ok = False
                try:
                    ok = instance in inner_type
                except Exception:
                    checker = getattr(inner_type, '__instancecheck__', None)
                    ok = isinstance(instance, inner_type) or (callable(checker) and checker(instance))
                if ok:
                    for cond in getattr(cls, '__conditions_list', []):
                        if not cond({key_name: instance}):
                            return False
                    return True
            return False

        attrs_types = dict(getattr(cls, '_required_attributes_and_types', ()))
        required_keys = set(getattr(cls, '_required_attribute_keys', set()))
        optional_attributes_and_defaults = getattr(cls, '_optional_attributes_and_defaults', {})

        for req_key in required_keys:
            if req_key not in instance:
                return False
            v = instance[req_key]
            expected_type = attrs_types.get(req_key)
            ok = False
            try:
                ok = v in expected_type
            except Exception:
                checker = getattr(expected_type, '__instancecheck__', None)
                ok = isinstance(v, expected_type) or (callable(checker) and checker(v))
            if not ok:
                return False

        for opt_name, wrapper in optional_attributes_and_defaults.items():
            if opt_name in instance:
                v = instance[opt_name]
                expected_type = wrapper.type
                ok = False
                try:
                    ok = v in expected_type
                except Exception:
                    checker = getattr(expected_type, '__instancecheck__', None)
                    ok = isinstance(v, expected_type) or (callable(checker) and checker(v))
                if not ok:
                    return False

        for cond in getattr(cls, '__conditions_list', []):
            if not cond(instance):
                return False

        return True

    def __subclasscheck__(cls, subclass):
        if not isinstance(subclass, type): return False
        if cls in getattr(subclass, '__mro__', []): return True
        if not all(hasattr(subclass, attr) for attr in ['_required_attributes_and_types', '_required_attribute_keys', '_optional_attributes_and_defaults']): return False
        if not isinstance(subclass, TYPE): return False

        cls_req_attrs = dict(getattr(cls, '_required_attributes_and_types', ()))
        sub_req_attrs = dict(getattr(subclass, '_required_attributes_and_types', ()))
        cls_opt_attrs = getattr(cls, '_optional_attributes_and_defaults', {})
        sub_opt_attrs = getattr(subclass, '_optional_attributes_and_defaults', {})

        if not set(cls_req_attrs.keys()).issubset(set(sub_req_attrs.keys()) | set(sub_opt_attrs.keys())): return False
        if not set(cls_opt_attrs.keys()).issubset(set(sub_req_attrs.keys()) | set(sub_opt_attrs.keys())): return False

        for name, p_type in cls_req_attrs.items():
            if name in sub_req_attrs:
                if not issubclass(sub_req_attrs[name], p_type): return False
            elif name in sub_opt_attrs:
                if not issubclass(sub_opt_attrs[name].type, p_type): return False

        for name, p_wrapper in cls_opt_attrs.items():
            p_type = p_wrapper.type
            if name in sub_req_attrs:
                if not issubclass(sub_req_attrs[name], p_type): return False
            elif name in sub_opt_attrs:
                s_wrapper = sub_opt_attrs[name]
                if not issubclass(s_wrapper.type, p_type): return False
                if not isinstance(s_wrapper.default_value, p_type): return False

        if not set(getattr(cls, '__conditions_list', [])).issubset(set(getattr(subclass, '__conditions_list', []))): return False
        return True

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

        for req_key in self.__class__._defined_required_attributes:
            if req_key not in self:
                 raise TypeError(f"Missing required attribute '{req_key}' for exact model {self.__class__.__name__}")

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
        if name not in self._all_possible_keys:
            raise AttributeError(f"'{self.__class__.__name__}' is an exact model, attribute '{name}' not allowed.")
        if name in self._defined_required_attributes:
            expected_type = self._defined_required_attributes[name]
            if not isinstance(value, expected_type):
                raise TypeError(f"Attribute '{name}' requires type '{_name(expected_type)}', got '{_name(type(value))}'")
            self[name] = value
        elif name in self._defined_optional_attributes:
            expected_type = self._defined_optional_attributes[name].type
            if not isinstance(value, expected_type):
                raise TypeError(f"Attribute '{name}' requires type '{_name(expected_type)}', got '{_name(type(value))}'")
            self[name] = value
        else:
            object.__setattr__(self, name, value)

    @property
    def __json__(self):
        from typed.mods.helper.models import _to_json
        return _to_json(self)


class EXACT_META(_MODEL_FACTORY_, _EXACT_, _MODEL_INSTANCE_):
    def __new__(cls, name, bases, dct):
        new_type = super().__new__(cls, name, bases, dct)
        attrs_types = dict(dct.get('_initial_attributes_and_types', ()))
        opt_attrs = dct.get('_initial_optional_attributes_and_defaults', {})
        setattr(new_type, '_defined_required_attributes', {k: v for k, v in attrs_types.items() if k not in opt_attrs})
        setattr(new_type, '_defined_optional_attributes', opt_attrs)
        all_keys = set(attrs_types.keys())
        setattr(new_type, '_defined_keys', all_keys)
        setattr(new_type, '_all_possible_keys', dct.get('_initial_all_possible_keys', set()))
        setattr(new_type, '_required_attributes_and_types', dct.get('_initial_attributes_and_types', ()))
        setattr(new_type, '_required_attribute_keys', dct.get('_initial_required_attribute_keys', set()))
        setattr(new_type, '_optional_attributes_and_defaults', opt_attrs)
        setattr(new_type, '__conditions_list', dct.get('_initial_conditions', []))
        return new_type

    def __init__(cls, name, bases, dct):
        for key in ['_initial_attributes_and_types', '_initial_required_attribute_keys',
                    '_initial_optional_attributes_and_defaults', '_initial_all_possible_keys', '_initial_conditions']:
            if key in dct:
                del dct[key]
        super().__init__(name, bases, dct)

    def __instancecheck__(cls, instance):
        if not isinstance(instance, Dict):
            all_keys = getattr(cls, '_all_possible_keys', set())
            if len(all_keys) == 1:
                inner_type, key_name = _single_field_inner_type_and_key(cls)
                if inner_type is not None:
                    ok = False
                    try:
                        ok = instance in inner_type
                    except Exception:
                        checker = getattr(inner_type, '__instancecheck__', None)
                        ok = isinstance(instance, inner_type) or (callable(checker) and checker(instance))
                    if ok:
                        for cond in getattr(cls, '__conditions_list', []):
                            if not cond({key_name: instance}):
                                return False
                        return True
            return False

        if not isinstance(instance, Dict):
            return False

        instance_keys = set(instance.keys())
        expected_keys = getattr(cls, '_all_possible_keys', set())
        if instance_keys != expected_keys:
            return False

        req = dict(getattr(cls, '_required_attributes_and_types', ()))
        opt = getattr(cls, '_optional_attributes_and_defaults', {})

        for k in expected_keys:
            v = instance[k]
            if k in req:
                typ = req[k]
            elif k in opt:
                typ = opt[k].type
            else:
                return False
            if not isinstance(v, typ):
                checker = getattr(typ, '__instancecheck__', None)
                if not (callable(checker) and checker(v)):
                    return False

        for cond in getattr(cls, '__conditions_list', []):
            if not cond(instance):
                return False

        return True

    def __subclasscheck__(cls, subclass):
        if not isinstance(subclass, type) or not getattr(subclass, 'is_model', False): return False
        cls_keys = getattr(cls, '_all_possible_keys', set())
        sub_keys = getattr(subclass, '_all_possible_keys', set())
        if cls_keys != sub_keys: return False

        return super().__subclasscheck__(cls, subclass) if hasattr(super(), '__subclasscheck__') else True

class ORDERED_INSTANCE(Dict, metaclass=_MODEL_INSTANCE_):
    _ordered_keys = []
    _defined_required_attributes = {}
    _defined_optional_attributes = {}
    _defined_keys = set()

    def __init__(self, **data):
        super().__init__()
        if list(data.keys()) != [k for k in self._ordered_keys if k in data]:
            raise TypeError(f"Input keys order {list(data.keys())} does not match expected order prefix in model: {self._ordered_keys}")

        for key, wrapper in self._defined_optional_attributes.items():
            super().__setitem__(key, wrapper.default_value)
        for key, value in data.items():
            self.__setattr__(key, value)
        for req_key in self._defined_required_attributes.keys():
            if req_key not in self:
                raise TypeError(f"Missing required attribute '{req_key}' during initialization.")

    def __setattr__(self, name, value):
        if name in self._defined_required_attributes:
            expected_type = self._defined_required_attributes[name]
            if not isinstance(value, expected_type):
                raise TypeError(f"Attribute '{name}' type mismatch: expected {_name(expected_type)}, got {_name(type(value))}")
            self[name] = value
        elif name in self._defined_optional_attributes:
            expected_type = self._defined_optional_attributes[name].type
            if not isinstance(value, expected_type):
                raise TypeError(f"Attribute '{name}' type mismatch: expected {_name(expected_type)}, got {_name(type(value))}")
            self[name] = value
        else:
            object.__setattr__(self, name, value)

    @property
    def __json__(self):
        from typed.mods.helper.models import _to_json
        return _to_json(self)

class ORDERED_META(_MODEL_FACTORY_, _ORDERED_, _MODEL_INSTANCE_):
    def __new__(cls, name, bases, dct):
        new_type = super().__new__(cls, name, bases, dct)
        attrs_types = dict(dct.get('_initial_attributes_and_types', ()))
        opt_attrs = dct.get('_initial_optional_attributes_and_defaults', {})
        setattr(new_type, '_defined_required_attributes', {k:v for k,v in attrs_types.items() if k not in opt_attrs})
        setattr(new_type, '_defined_optional_attributes', opt_attrs)
        setattr(new_type, '_ordered_keys', dct.get('_initial_ordered_keys'))
        setattr(new_type, '__conditions_list', dct.get('_initial_conditions', []))
        setattr(new_type, '_required_attributes_and_types', dct.get('_initial_attributes_and_types', ()))
        setattr(new_type, '_optional_attributes_and_defaults', opt_attrs)
        setattr(new_type, '_defined_keys', set(attrs_types.keys()))
        return new_type

    def __init__(cls, name, bases, dct):
        for key in ['_initial_attributes_and_types', '_initial_optional_attributes_and_defaults', '_initial_ordered_keys', '_initial_conditions']:
            if key in dct:
                del dct[key]
        super().__init__(name, bases, dct)

    def __instancecheck__(cls, instance):
        if not isinstance(instance, Dict):
            model_keys = getattr(cls, '_ordered_keys', [])
            if len(model_keys) == 1:
                inner_type, key_name = _single_field_inner_type_and_key(cls)
                if inner_type is not None:
                    ok = False
                    try:
                        ok = instance in inner_type
                    except Exception:
                        checker = getattr(inner_type, '__instancecheck__', None)
                        ok = isinstance(instance, inner_type) or (callable(checker) and checker(instance))
                    if ok:
                        for cond in getattr(cls, '__conditions_list', []):
                            if not cond({key_name: instance}):
                                return False
                        return True
            return False

        if not isinstance(instance, Dict):
            return False

        instance_keys = list(instance.keys())
        model_keys = getattr(cls, '_ordered_keys', [])
        if len(instance_keys) > len(model_keys) or instance_keys != model_keys[:len(instance_keys)]:
            return False

        req = dict(getattr(cls, '_required_attributes_and_types', ()))
        opt = getattr(cls, '_optional_attributes_and_defaults', {})

        for k in instance_keys:
            v = instance[k]
            if k in req:
                typ = req[k]
            elif k in opt:
                typ = opt[k].type
            else:
                return False
            if not isinstance(v, typ):
                checker = getattr(typ, '__instancecheck__', None)
                if not (callable(checker) and checker(v)):
                    return False

        for cond in getattr(cls, '__conditions_list', []):
            if not cond(instance):
                return False

        return True

    def __subclasscheck__(cls, subclass):
        if not isinstance(subclass, type) or not hasattr(subclass, '_ordered_keys'): return False
        cls_keys = getattr(cls, '_ordered_keys', [])
        sub_keys = getattr(subclass, '_ordered_keys', [])
        return sub_keys[:len(cls_keys)] == cls_keys

class RIGID_INSTANCE(Dict, metaclass=_MODEL_INSTANCE_):
    _ordered_keys = []
    _defined_required_attributes = {}
    _defined_optional_attributes = {}

    def __init__(self, **data):
        super().__init__()
        if list(data.keys()) != self._ordered_keys:
            raise TypeError(f"Input keys order/set {list(data.keys())} does not match rigid model order: {self._ordered_keys}")

        for key in self._ordered_keys:
            if key in data:
                self.__setattr__(key, data[key])
            elif key in self._defined_optional_attributes:
                self.__setattr__(key, self._defined_optional_attributes[key].default_value)

        for req_key in self._defined_required_attributes:
            if req_key not in self:
                raise TypeError(f"Missing required attribute '{req_key}' for rigid model initialization.")

    def __setattr__(self, name, value):
        if name not in self._ordered_keys:
            raise AttributeError(f"'{name}' is not a valid attribute for this rigid model.")

        expected_type = None
        if name in self._defined_required_attributes: expected_type = self._defined_required_attributes[name]
        elif name in self._defined_optional_attributes: expected_type = self._defined_optional_attributes[name].type

        if expected_type and not isinstance(value, expected_type):
            raise TypeError(f"Attribute '{name}' type mismatch: expected {_name(expected_type)}, got {_name(type(value))}")

        self[name] = value

    @property
    def __json__(self):
        from typed.mods.helper.models import _to_json
        return _to_json(self)

class RIGID_META(_MODEL_FACTORY_, _RIGID_, _MODEL_INSTANCE_):
    def __new__(cls, name, bases, dct):
        new_type = super().__new__(cls, name, bases, dct)
        attrs_types = dict(dct.get('_initial_attributes_and_types', ()))
        opt_attrs = dct.get('_initial_optional_attributes_and_defaults', {})
        ordered_keys = dct.get('_initial_ordered_keys', [])

        setattr(new_type, '_ordered_keys', ordered_keys)
        setattr(new_type, '_defined_required_attributes', {k: v for k, v in attrs_types.items() if k not in opt_attrs})
        setattr(new_type, '_defined_optional_attributes', opt_attrs)
        setattr(new_type, '_defined_keys', set(attrs_types.keys()))
        setattr(new_type, '_required_attributes_and_types', dct.get('_initial_attributes_and_types', ()))
        setattr(new_type, '_optional_attributes_and_defaults', opt_attrs)
        setattr(new_type, '__conditions_list', dct.get('_initial_conditions', []))
        setattr(new_type, '_all_possible_keys', set(ordered_keys))
        setattr(new_type, '_required_attribute_keys', dct.get('_initial_required_attribute_keys', set()))
        return new_type

    def __init__(cls, name, bases, dct):
        keys_to_del = ['_initial_attributes_and_types', '_initial_optional_attributes_and_defaults',
                       '_initial_ordered_keys', '_initial_required_attribute_keys', '_initial_conditions']
        for key in keys_to_del:
            if key in dct:
                del dct[key]
        super().__init__(name, bases, dct)

    def __instancecheck__(cls, instance):
        if not isinstance(instance, Dict):
            model_keys = getattr(cls, '_ordered_keys', [])
            if len(model_keys) == 1:
                inner_type, key_name = _single_field_inner_type_and_key(cls)
                if inner_type is not None:
                    ok = False
                    try:
                        ok = instance in inner_type
                    except Exception:
                        checker = getattr(inner_type, '__instancecheck__', None)
                        ok = isinstance(instance, inner_type) or (callable(checker) and checker(instance))
                    if ok:
                        for cond in getattr(cls, '__conditions_list', []):
                            if not cond({key_name: instance}):
                                return False
                        return True
            return False

        if not isinstance(instance, Dict):
            return False

        instance_keys = list(instance.keys())
        ordered_keys = getattr(cls, '_ordered_keys', [])
        if instance_keys != ordered_keys:
            return False

        req = dict(getattr(cls, '_required_attributes_and_types', ()))
        opt = getattr(cls, '_optional_attributes_and_defaults', {})

        for k in instance_keys:
            v = instance[k]
            if k in req:
                typ = req[k]
            elif k in opt:
                typ = opt[k].type
            else:
                return False
            if not isinstance(v, typ):
                checker = getattr(typ, '__instancecheck__', None)
                if not (callable(checker) and checker(v)):
                    return False

        for cond in getattr(cls, '__conditions_list', []):
            if not cond(instance):
                return False

        return True 

    def __subclasscheck__(cls, subclass):
        if not isinstance(subclass, type) or not hasattr(subclass, '_ordered_keys'): return False
        return getattr(cls, '_ordered_keys', []) == getattr(subclass, '_ordered_keys', [])
