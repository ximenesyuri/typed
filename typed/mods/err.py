def notify(message, handler=None, __multiline__=False, **kwargs):
    full_message = str(message)

    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}

    if filtered_kwargs:
        full_message = full_message.rstrip(":") + ":"

        if __multiline__:
            parts = [f"\n    {k}: {v}" for k, v in filtered_kwargs.items()]
            full_message += "".join(parts)
        else:
            parts = [f"{k}={v!r}" for k, v in filtered_kwargs.items()]
            full_message += " " + ", ".join(parts) + "."

    if handler is None:
        return full_message

    if isinstance(handler, type) and issubclass(handler, BaseException):
        raise handler(full_message)

    handler(full_message)
    return None


class Err(BaseException):
    def __init__(self, message, **kwargs):
        __message__ = notify(message=message, **kwargs)
        super().__init__(__message__)

class NotDefined(Err): pass
class Anonymous(Err): pass

class FuncErr(Err):
    def __init__(self, message="Error in function", details=NotDefined, func=NotDefined, **kwargs):
        if func is NotDefined:
            raise AttributeError("Missing 'func' arg in 'FuncErr'.")

        from typed.mods.core import name
        func = name(func)

        kwargs.setdefault("__multiline__", True)

        if details is not NotDefined:
            super().__init__(
                message=message,
                details=details,
                func=func,
                **kwargs
            )
        else:
            super().__init__(
                message=message,
                func=func,
                **kwargs
            )

class HintErr(Err):
    def __init__(
        self,
        message="Missing type hint",
        term=None,
        args=None,
        **kwargs
    ):
        if term is None:
            raise ValueError("Missing 'term' in 'HintErr'.")

        from typed.mods.core import name
        term = name(term)

        if args is not None:
            if isinstance(args, tuple):
                args = tuple(name(a) for a in args)
            else:
                args = name(args)
            kwargs["args"] = args

        kwargs.setdefault("__multiline__", True)

        super().__init__(
            message=message,
            term=term,
            **kwargs
        )


class TypeErr(Err):
    def __init__(
        self,
        message="Wrong term type identified",
        term=None,
        args=None,
        received=None,
        expected=None,
        **kwargs
    ):
        if term is None:
            raise ValueError("Missing 'term' in 'TypeErr'.")
        if received is None:
            raise ValueError("Missing 'received' in 'TypeErr'")
        if expected is None:
            raise ValueError("Missing 'expected' in 'TypeErr'")

        from typed.mods.core import name, type

        term_type = type(term)
        term_typesystems = getattr(term_type, "__typesystems__", [])

        if not term_typesystems:
            raise AttributeError(f"The term '{name(term)}' has a type '{name(term_type)}' with no defined typesystem.")

        if args is not None:
            message = "Wrong argument type identified"
            if isinstance(args, tuple):
                if not isinstance(received, tuple) or len(received) != len(args):
                    raise ValueError("'received' must be a tuple of the same length as 'args'.")
                if not isinstance(expected, tuple) or len(expected) != len(args):
                    raise ValueError("'expected' must be a tuple of the same length as 'args'.")

        term = name(term)
        typesystems = ", ".join(name(t) for t in term_typesystems)

        if args is not None:
            if isinstance(args, tuple):
                args = tuple(name(a) for a in args)
                received = tuple(name(r) for r in received)
                expected = tuple(name(e) for e in expected)
            else:
                args = name(args)
                received = name(received)
                expected = name(expected)
            kwargs["args"] = args
        else:
            received = name(received)
            expected = name(expected)

        kwargs.setdefault("__multiline__", True)

        super().__init__(
            message=message,
            term=term,
            received=received,
            expected=expected,
            **kwargs
        )

class DomErr(TypeErr):
    def __init__(self, message="Wrong domain type identified", term=None, args=None, received=None, expected=None, **kwargs):
        super().__init__(
            message=message,
            term=term,
            args=args,
            received=received,
            expected=expected,
            **kwargs
        )

class CodErr(TypeErr):
    def __init__(self, message="Wrong codomain type identified", term=None, args=None, received=None, expected=None, **kwargs):
        super().__init__(
            message=message, 
            term=term, 
            args=args, 
            received=received, 
            expected=expected, 
            **kwargs
        )
