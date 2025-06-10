from typing import Any, Type, List, Union

def Attr(attributes: Union[str, List[str]]) -> Type[Any]:
    if isinstance(attributes, str):
        attributes = (attributes,)
    elif not isinstance(attributes, list):
        raise TypeError("attributes must be a string or a list of strings")

    type_name = f'Attr{"_and_".join(attr.strip("_").capitalize() for attr in attributes)}'

    class __Attr(type):
        def __init__(cls, name, bases, dct, attributes=None):
            super().__init__(name, bases, dct)
            if attributes:
                setattr(cls, '_required_attributes', attributes)

        def __instancecheck__(cls, instance: Any) -> bool:
            required_attributes = getattr(cls, '_required_attributes', None)
            if required_attributes:
                return all(hasattr(instance, attr) for attr in required_attributes)
            return True

    class Attr__(metaclass=__Attr):
        pass

    return type(type_name, (Attr__,), {'_required_attributes': tuple(attributes)})


Callable            = Attr('__call__')
Iterable            = Attr('__iter__')
Iterator            = Attr('__next__')
Sized               = Attr('__len__')
Container           = Attr('__contains__')
Hashable            = Attr('__hash__')
Awaitable           = Attr('__await__')
AsyncIterable       = Attr('__aiter__')
AsyncIterator       = Attr('__anext__')
ContextManager      = Attr(['__enter__', '__exit__'])
AsyncContextManager = Attr(['__aenter__', '__aexit__'])


Callable.__display__            = "Callable"
Iterable.__display__            = "Iterable"
Iterator.__display__            = "Iterator"
Sized.__display__               = "Sized"
Container.__display__           = "Contains"
Hashable.__display__            = "Hashable"
Awaitable.__display__           = "Awaitable"
AsyncIterable.__display__       = "AsyncIterable"
AsyncIterator.__display__       = "AsyncIterator"
ContextManager.__display__      = "ContextManager"
AsyncContextManager.__display__ = "AsyncContextManager"
