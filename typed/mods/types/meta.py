import re

class _Any(type):
    def __instancecheck__(cls, instance):
        return True
    def __subclasscheck__(cls, subclass):
        return True

class _Pattern(type):
    def __instancecheck__(cls, instance):
        if not isinstance(instance, str):
            return False
        try:
            re.compile(instance)
            return True
        except re.error:
            return False
    def __repr__(cls):
        return "Pattern(str): a string valid as Python regex"

class _Meta(type):
    def __instancecheck__(cls, instance):
        return isinstance(instance, type) and issubclass(instance, type)
