from typing import Type, Any

class _OptionalWrapper:
    def __init__(self, type: Type, default_value: Any):
        self.type = type
        self.default_value = default_value
