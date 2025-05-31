from typing import Type, Any as Any_

class _OptionalWrapper:
    def __init__(self, type: Type, default_value: Any_):
        self.type = type
        self.default_value = default_value
