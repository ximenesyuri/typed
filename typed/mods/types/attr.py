from typing import List, Type

def Attr(*attributes: List[str]) -> Type:
    """
    Build the 'attributable type':
        > the objects of 'Attr(a1, a2, ...)' are the
        > classes 'X' such that 'getattr(X, a)' is True
        > for every 'a in (a1, a2, ...)'
    """
    if not attributes:
        return type

    class __Attr(type):
        def __init__(cls, name, bases, dct, attributes=None):
            super().__init__(name, bases, dct)
            if attributes:
                setattr(cls, '_attributes', attributes)

        def __instancecheck__(cls, instance):
            if not isinstance(instance, type):
                return False
            attributes = getattr(cls, '_attributes', None)
            if attributes:
                return all(hasattr(instance, attr) for attr in attributes)
            return False

    return __Attr(
        f'Supports_{"_and_".join(a.strip("_").capitalize() for a in attributes)}',
        (type),
        {},
        attributes=attributes
    )

Callable           = Attr('__call__')
Additive           = Attr('__add__')
Multiplicative     = Attr('__mul__')
Nullable           = Attr('__null__')
Appendable         = Attr('__append__')
Sized              = Attr('__len__')
Iterable           = Attr('__iter__')
Hashable           = Attr('__hash__')
Container          = Attr('__contains__')
MutableContainer   = Attr('__contains__', '__setitem__')
IndexedContainer   = Attr('__contains__', '__getitem__')
DeletableContainer = Attr('__contains__', '__delitem__')
