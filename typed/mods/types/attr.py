def ATTR(attributes):
    if isinstance(attributes, str):
        attributes = (attributes,)
    elif not isinstance(attributes, list):
        raise TypeError("attributes must be a string or a list of strings")

    type_name = f'ATTR{"_and_".join(attr.strip("_").capitalize() for attr in attributes)}'

    class _ATTR(type):
        def __init__(cls, name, bases, dct, attributes=None):
            super().__init__(name, bases, dct)
            if attributes:
                setattr(cls, '_required_attributes', attributes)

        def __instancecheck__(cls, instance):
            required_attributes = getattr(cls, '_required_attributes', None)
            if required_attributes:
                return all(hasattr(instance, attr) for attr in required_attributes)
            return True

    class ATTR_(metaclass=_ATTR):
        pass

    return type(type_name, (ATTR_,), {'_required_attributes': tuple(attributes)})

NULLABLE       = ATTR('__null__')
CALLABLE       = ATTR('__call__')
ITERABLE       = ATTR('__iter__')
ITERATOR       = ATTR('__next__')
SIZED          = ATTR('__len__')
CONTAINER      = ATTR('__contains__')
HASHABLE       = ATTR('__hash__')
AWAITABLE      = ATTR('__await__')
ASYNC_ITERABLE = ATTR('__aiter__')
ASYNC_ITERATOR = ATTR('__anext__')
CONTEXT        = ATTR(['__enter__', '__exit__'])
ASYNC_CONTEXT  = ATTR(['__aenter__', '__aexit__'])

NULLABLE.__display__       = "NULLABLE"
CALLABLE.__display__       = "CALLABLE"
ITERABLE.__display__       = "ITERABLE"
ITERATOR.__display__       = "ITERATOR"
SIZED.__display__          = "SIZED"
CONTAINER.__display__      = "CONTAINER"
HASHABLE.__display__       = "HASHABLE"
AWAITABLE.__display__      = "AWAITABLE"
ASYNC_ITERABLE.__display__ = "ASYNC_ITERABLE"
ASYNC_ITERATOR.__display__ = "ASYNC_ITERATOR"
CONTEXT.__display__        = "CONTEXT"
ASYNC_CONTEXT.__display__  = "ASYNC_CONTEXT"
