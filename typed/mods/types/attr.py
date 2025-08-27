from typed.mods.helper.helper import _name_list

def ATTR(attributes):
    if isinstance(attributes, str):
        attributes = (attributes,)
    elif not isinstance(attributes, list):
        raise TypeError("attributes must be a string or a list of strings")

    class _ATTR_(type):
        def __init__(cls, name, bases, dct, attributes=None):
            super().__init__(name, bases, dct)
            if attributes:
                setattr(cls, '__attrs__', attributes)

        def __instancecheck__(cls, instance):
            attrs = getattr(cls, '__attrs__', None)
            if attrs:
                return all(hasattr(instance, attr) for attr in attrs)
            return False

    class_name = f'ATTR({_name_list(*attributes)})'

    from typed.mods.types.base import Nill
    return _ATTR_(class_name, (), {
        '__attrs__': tuple(attributes),
        "__null__": Nill,
        "__display__": class_name
    })
