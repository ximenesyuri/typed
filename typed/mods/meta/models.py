from typed.mods.meta.base import _TYPE_, DICT
from typed.mods.meta.func import FACTORY
from typed.mods.types.base import TYPE, Str, Set, Dict
from typed.mods.helper.helper import _issubtype

class _MODEL_INSTANCE_(DICT):
    def __instancecheck__(cls, instance):
        if not instance in Dict:
            return False

class _MODEL_FACTORY_(FACTORY):
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
