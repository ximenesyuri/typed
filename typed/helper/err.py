def _message(message="", handler=None, **kwargs):
    if not kwargs:
        full_message = message
    else:
        full_message = message.rstrip(":") + ":"
        parts = [f"{k}={v!r}" for k, v in kwargs.items()]
        full_message += " " + ", ".join(parts)
        full_message += "."

    if handler is None:
        return full_message

    if isinstance(handler, type) and issubclass(handler, BaseException):
        raise handler(full_message)

    handler(full_message)
    return None
