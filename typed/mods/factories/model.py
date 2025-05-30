from typing import Type
from typed.mods.types.base import Json, Any

def Model(**kwargs: Type) -> Type[Json]:
    """
    Build a 'model' which is a subclass of Json.
        > An object 'x' is an instance of Model(arg1: Type1, arg2: Type2, ...) iff:
            1. isinstance(x, Json) is True
            2. x is a dictionary
            3. x.get(arg1) has type Type1, x.get(arg2) has type Type2, ...

    Concatenation of Models is supported.
    """
    if not kwargs:
        raise TypeError("Model factory requires at least one argument.")

    if not all(isinstance(key, str) for key in kwargs.keys()):
        raise TypeError("All arguments to Model must be strings representing attribute names.")

    if not all(isinstance(value, type) or hasattr(value, '__instancecheck__') for value in kwargs.values()):
       valid_types = [k for k, v in kwargs.items() if not (isinstance(v, type) or hasattr(v, '__instancecheck__'))]
       raise TypeError(f"All argument values must be types. Invalid types for: {', '.join(valid_types)}")

    attributes_and_types = tuple(kwargs.items())

    class __Model(type(Json)):
        def __init__(cls, name, bases, dct, attributes_and_types=None):
            super().__init__(name, bases, dct)
            if attributes_and_types is not None:
                setattr(cls, '_required_attributes_and_types', attributes_and_types)

        def __instancecheck__(cls, instance: Any) -> bool:
            if not isinstance(instance, dict):
                return False

            required_attributes_and_types = getattr(cls, '_required_attributes_and_types', ())

            for attr_name, expected_type in required_attributes_and_types:
                if attr_name not in instance:
                    return False
                attr_value = instance.get(attr_name)

                if not isinstance(attr_value, expected_type):
                    if isinstance(expected_type, __class__):
                        if not expected_type.__instancecheck__(attr_value):
                            return False
                    else:
                        return False

            return True

        def __subclasscheck__(cls, subclass: Type) -> bool:
            if not issubclass(subclass, Json):
                return False

            if not hasattr(subclass, '_required_attributes_and_types'):
                return False

            cls_attrs = dict(getattr(cls, '_required_attributes_and_types', ()))
            subclass_attrs = dict(getattr(subclass, '_required_attributes_and_types', ()))

            if not set(cls_attrs.keys()).issubset(set(subclass_attrs.keys())):
                return False

            for attr_name, parent_type in cls_attrs.items():
                subclass_type = subclass_attrs[attr_name]
                if not issubclass(subclass_type, parent_type):
                    return False

            return True

    args_str = ", ".join(f"{key}: {getattr(value, '__name__', str(value))}" for key, value in attributes_and_types)
    class_name = f"Model({args_str})"

    return __Model(class_name, (Json,), {}, attributes_and_types=attributes_and_types)
