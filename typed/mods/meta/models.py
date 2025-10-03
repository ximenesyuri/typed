from typed.mods.meta.base import _TYPE_, DICT
from typed.mods.meta.func import FACTORY
from typed.mods.types.base import TYPE, Str, Set, Dict
from typed.mods.helper.helper import _issubtype, _name

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
            from typed.models import Validate
            Validate(entity_dict, cls)
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
