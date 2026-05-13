from typed.helper.err import _message

class Err(BaseException):
    def __init__(self, message="", **kwargs):
        if message or kwargs:
            formatted_message = _message(message=message, **kwargs)
            super().__init__(formatted_message)
        else:
            super().__init__()

class TypedErr(Err): pass

class NotDefined(Err): pass

class UniverseErr(TypedErr): pass
