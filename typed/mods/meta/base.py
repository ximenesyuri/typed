import re
from typed.mods.helper.helper import _name

class _TYPE_(type(type)):
    def __instancecheck__(cls, instance):
        return isinstance(instance, type)

    def __subclasscheck__(cls, instance):
        return issubclass(instance, type)

    def __call__(cls, obj):
        from typed.mods.types.base import Str, Int, Float, Bool, Nill, Any
        from typed.mods.types.factories import List, Tuple, Set, Dict
        types_map = {
            type(None): Nill,
            bool: Bool,
            int: Int,
            float: Float,
            str: Str,
            list: List(Any),
            tuple: Tuple(Any),
            dict: Dict(Any),
            set: Set(Any)
        }
        for k, v in types_map.items():
            if type(obj) is k:
                return v
        return type(obj)

class NILL(type(type(None))):
    def __instancecheck__(cls, instance):
        return False

    def __subclasscheck__(cls, instance):
        return False

class INT(type(int)):
    def __instancecheck__(cls, instance):
        return isinstance(instance, int)

    def __subclasscheck__(cls, instance):
        return issubclass(instance, int)

    def __convert__(cls, obj):
        from typed.mods.types.base import TYPE
        from typed.mods.types.attr import ATTR
        from typed.mods.helper.helper import _name
        if isinstance(TYPE(obj), ATTR('__int__')):
            return int(obj)
        raise TypeError(
            "Wrong type in Int function.\n"
            f" ==> '{obj}': has an unexpected type."
            f"     [expected_type] an instance of {_name(ATTR('__int__'))}"
            f"     [received_type] {_name(TYPE(obj))}"
        )

class FLOAT(type(float)):
    def __instancecheck__(cls, instance):
        return isinstance(instance, float)

    def __subclasscheck__(cls, instance):
        return issubclass(instance, float)

    def __convert__(cls, obj):
        from typed.mods.types.base import TYPE
        from typed.mods.types.attr import ATTR
        from typed.mods.helper.helper import _name
        if isinstance(TYPE(obj), ATTR('__float__')):
            return float(obj)
        raise TypeError(
            "Wrong type in Float function.\n"
            f" ==> '{obj}': has an unexpected type."
            f"     [expected_type] an instance of {_name(ATTR('__int__'))}"
            f"     [received_type] {_name(TYPE(obj))}"
        )

class STR(type(str)):
    def __instancecheck__(cls, instance):
        return isinstance(instance, str)

    def __subclasscheck__(cls, instance):
        return issubclass(instance, str)

class BOOL(type(bool)):
    def __instancecheck__(cls, instance):
        return isinstance(instance, bool)

    def __subclasscheck__(cls, instance):
        return issubclass(instance, bool)

class ANY(type):
    def __instancecheck__(cls, instance):
        return True
    def __subclasscheck__(cls, subclass):
        return True

class PATTERN(STR):
    def __instancecheck__(cls, instance):
        if not isinstance(instance, str):
            return False
        try:
            re.compile(instance)
            return True
        except re.error:
            return False
    def __repr__(cls):
        return "Pattern(str): a string valid as Python regex"

class _META_(_TYPE_):
    def __instancecheck__(self, instance):
        return isinstance(instance, type) and issubclass(instance, type)
