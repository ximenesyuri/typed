from typed.mods.meta.base import _TYPE_, DICT
from typed.mods.meta.func import FACTORY
from typed.mods.types.base import TYPE, Set, Dict
from typed.mods.helper.helper import _issubtype, _name


def _single_field_inner_type_and_key(mcls):
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


class _ModelKeys:
    def __get__(self, obj, owner=None):
        if owner is None:
            return lambda: ()

        if obj is None:
            cls = owner

            def _keys():
                attrs = getattr(cls, 'attrs', None)
                if attrs is None:
                    return ()
                ordered = getattr(cls, '_ordered_keys', None)
                if ordered:
                    return tuple(k for k in ordered if k in attrs)
                return tuple(attrs.keys())
            return _keys

        inst = obj
        cls = owner

        def _keys():
            return inst.__json__.keys()

        return _keys


class _ModelValues:
    def __get__(self, obj, owner=None):
        if owner is None:
            return lambda: ()

        if obj is None:
            cls = owner

            def _values():
                attrs = getattr(cls, 'attrs', None)
                if attrs is None:
                    return ()
                return tuple(attrs[k]['type'] for k in cls.keys())
            return _values

        inst = obj
        cls = owner

        def _values():
            return inst.__json__.values()
        return _values


class _ModelItems:
    def __get__(self, obj, owner=None):
        if owner is None:
            return lambda: ()
        if obj is None:
            cls = owner

            def _items():
                attrs = getattr(cls, 'attrs', None)
                if attrs is None:
                    return ()
                return tuple((k, attrs[k]['type']) for k in cls.keys())
            return _items

        inst = obj
        cls = owner

        def _items():
            return inst.__json__.items()

        return _items


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
                raise TypeError(
                    "Received wrong type in cls.:\n"
                    f" ==> '{args[0].__name__}': has value '{_name(entity)}'\n"
                     "     [expected_type] Dict\n"
                    f"     [received_type] {_name(type(entity))}"
                )
            entity_dict = entity.copy()
        else:
            entity_dict = kwargs

        optional_defaults = getattr(cls, '_optional_attributes_and_defaults', {})
        for attr, wrapper in optional_defaults.items():
            if attr not in entity_dict:
                entity_dict[attr] = wrapper.default_value

        required_types = dict(getattr(cls, '_required_attributes_and_types', ()))
        optional_wrappers = getattr(cls, '_optional_attributes_and_defaults', {})

        for key, val in list(entity_dict.items()):
            target_type = None
            if key in required_types:
                target_type = required_types[key]
            elif key in optional_wrappers:
                target_type = optional_wrappers[key].type

            if target_type is None:
                continue

            if getattr(target_type, 'is_model', False) and isinstance(val, dict):
                entity_dict[key] = target_type(**val)

        if not cls.__instancecheck__(entity_dict):
            from typed.mods.models import validate
            validate(entity_dict, cls)
        obj = cls.__new__(cls)
        obj.__init__(**entity_dict)
        return obj


class _MODEL_(_TYPE_):
    def __instancecheck__(cls, instance):
        is_model = getattr(instance, 'is_model', False)
        if not is_model:
            return False

        is_lazy = getattr(instance, 'is_lazy', False)
        if is_lazy:
            real = getattr(instance, '_real_model', None)
            return real is not None

        return True

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

class _LAZY_MODEL_(_TYPE_):
    def __instancecheck__(cls, instance):
        if not getattr(instance, 'is_lazy', False):
            return False
        real = getattr(instance, '_real_model', None)
        return real is None

class _LAZY_EXACT_(_LAZY_MODEL_):
    def __instancecheck__(cls, instance):
        return getattr(instance, 'is_exact', False)

class _LAZY_ORDERED_(_LAZY_MODEL_):
    def __instancecheck__(cls, instance):
        return getattr(instance, 'is_ordered', False)

class _LAZY_RIGID_(_LAZY_EXACT_, _LAZY_ORDERED_):
    def __instancecheck__(cls, instance):
        return getattr(instance, 'is_rigid', False)

class MODEL_INSTANCE(Dict, metaclass=_MODEL_INSTANCE_):
    _defined_required_attributes = {}
    _defined_optional_attributes = {}
    _defined_keys: set = set()
    _ordered_keys: list = []

    def __init__(self, **data):
        super().__init__()
        # Initialize optional attributes with default values
        for key, wrapper in self.__class__._defined_optional_attributes.items():
            super().__setitem__(key, wrapper.default_value)
        # Set provided values
        for key, value in data.items():
            self.__setattr__(key, value)
        # Ensure all required attributes are present
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

    keys = _ModelKeys()
    values = _ModelValues()
    items = _ModelItems()


class MODEL_META(_MODEL_FACTORY_, _MODEL_, _MODEL_INSTANCE_):
    def __new__(cls, name, bases, dct):
        attrs_tuple  = dct.get('_initial_attributes_and_types', ())
        req_keys     = dct.get('_initial_required_attribute_keys', set())
        opt_dict     = dct.get('_initial_optional_attributes_and_defaults', {})
        conditions   = dct.get('_initial_conditions', [])
        ordered_keys = dct.get('_initial_ordered_keys', [])

        if req_keys:
            req_dict = {k: v for k, v in attrs_tuple if k in req_keys}
        else:
            req_dict = dict(attrs_tuple)

        defined_keys = set(req_dict.keys()) | set(opt_dict.keys())

        new_type = super().__new__(cls, name, bases, dct)

        setattr(new_type, '_defined_required_attributes', req_dict)
        setattr(new_type, '_defined_optional_attributes', opt_dict)
        setattr(new_type, '_defined_keys', defined_keys)
        setattr(new_type, '_required_attributes_and_types', attrs_tuple)
        setattr(new_type, '_required_attribute_keys', req_keys)
        setattr(new_type, '_optional_attributes_and_defaults', opt_dict)
        setattr(new_type, '__conditions_list', conditions)
        setattr(new_type, '_ordered_keys', ordered_keys)

        return new_type

    def __init__(cls, name, bases, dct):
        for key in [
            '_initial_attributes_and_types',
            '_initial_required_attribute_keys',
            '_initial_optional_attributes_and_defaults',
            '_initial_conditions',
            '_initial_ordered_keys',
        ]:
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

        req = getattr(cls, '_defined_required_attributes', {})
        opt = getattr(cls, '_defined_optional_attributes', {})
        optional_attributes_and_defaults = opt

        for req_key, expected_type in req.items():
            if req_key not in instance:
                return False
            v = instance[req_key]
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
        if not isinstance(subclass, type):
            return False
        if cls in getattr(subclass, '__mro__', []):
            return True

        if not all(
            hasattr(subclass, attr)
            for attr in ['_required_attributes_and_types',
                         '_required_attribute_keys',
                         '_optional_attributes_and_defaults']
        ):
            return False

        cls_req_attrs = getattr(cls, '_defined_required_attributes', {})
        sub_req_attrs = getattr(subclass, '_defined_required_attributes', {})
        cls_opt_attrs = getattr(cls, '_defined_optional_attributes', {})
        sub_opt_attrs = getattr(subclass, '_defined_optional_attributes', {})

        sub_all_keys = set(sub_req_attrs.keys()) | set(sub_opt_attrs.keys())

        if not set(cls_req_attrs.keys()).issubset(sub_all_keys):
            return False
        if not set(cls_opt_attrs.keys()).issubset(sub_all_keys):
            return False

        for name, p_type in cls_req_attrs.items():
            if name in sub_req_attrs:
                if not issubclass(sub_req_attrs[name], p_type):
                    return False
            elif name in sub_opt_attrs:
                if not issubclass(sub_opt_attrs[name].type, p_type):
                    return False

        for name, p_wrapper in cls_opt_attrs.items():
            p_type = p_wrapper.type
            if name in sub_req_attrs:
                if not issubclass(sub_req_attrs[name], p_type):
                    return False
            elif name in sub_opt_attrs:
                s_wrapper = sub_opt_attrs[name]
                if not issubclass(s_wrapper.type, p_type):
                    return False
                if not isinstance(s_wrapper.default_value, p_type):
                    return False

        if not set(getattr(cls, '__conditions_list', [])).issubset(
            set(getattr(subclass, '__conditions_list', []))
        ):
            return False

        return True

    @property
    def __json__(cls):
        from typed.mods.helper.models import _model_to_json
        return _model_to_json(cls)

class EXACT_INSTANCE(MODEL_INSTANCE): pass

class EXACT_META(MODEL_META):
    def __instancecheck__(cls, instance):
        return MODEL_META.__instancecheck__(cls, instance)

class ORDERED_INSTANCE(MODEL_INSTANCE): pass

class ORDERED_META(MODEL_META):
    def __instancecheck__(cls, instance):
        return MODEL_META.__instancecheck__(cls, instance)

class RIGID_INSTANCE(MODEL_INSTANCE): pass

class RIGID_META(MODEL_META):
    def __instancecheck__(cls, instance):
        return MODEL_META.__instancecheck__(cls, instance)

class LAZY_META(MODEL_META):
    def __new__(mcls, name, bases, namespace, **kw):
        cls = super().__new__(mcls, name, bases, namespace)
        cls._real_model = None
        return cls

    def _materialize(cls):
        real = cls._real_model
        if real is None:
            builder = super(LAZY_META, cls).__getattribute__('__builder__')
            real = builder()
            cls._real_model = real
        return real

    def __call__(cls, *args, **kwargs):
        real = cls._materialize()
        return real(*args, **kwargs)

    def __getattr__(cls, name):
        if name in ('_real_model', '__builder__', '__lazy_model__'):
            raise AttributeError
        real = cls._materialize()
        return getattr(real, name)

    def __instancecheck__(cls, instance):
        real = cls._materialize()
        return isinstance(instance, real)

    def __subclasscheck__(cls, subclass):
        if getattr(subclass, 'is_lazy', False):
            from typed.mods.helper.models import _lazy_submodel
            if _lazy_submodel(subclass, cls):
                return True

        real_cls = cls._materialize()

        if getattr(subclass, 'is_lazy', False) and hasattr(subclass, '_materialize'):
            real_sub = subclass._materialize()
        else:
            real_sub = subclass

        return issubclass(real_sub, real_cls)

    def __repr__(cls):
        return f"<LazyModel for {getattr(cls, '__name__', 'anonymous')}>"
