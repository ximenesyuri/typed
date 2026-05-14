from typed.helper.err import _message

class Err(BaseException):
    def __init__(self, message="", **kwargs):
        if message or kwargs:
            formatted_message = _message(message=message, **kwargs)
            super().__init__(formatted_message)
        else:
            super().__init__()

class FuncErr(Err): pass
class DomErr(Err): pass
class CodErr(Err): pass

class TypedErr(Err): pass

class TypeSystemErr(Err): pass
class UniverseErr(TypeSystemErr): pass
class AbstractErr(TypeSystemErr): pass

class NotDefined(Err): pass
class Anonymous(Err): pass
