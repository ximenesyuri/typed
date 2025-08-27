import re
from typed.mods.types.attr import ATTR
from typed.mods.helper.helper import _name

def poly(special_method: str, num_args=-1):
    pattern = r'^__.*__$'
    if not bool(re.match(pattern, special_method)):
        raise TypeError

    base_type = ATTR(special_method)

    if num_args == 0:
        def _poly(typ):
            if not isinstance(typ, base_type):
                return TypeError
            return getattr(type, special_method)
        return _poly

    def _poly(*args):
        if not args:
            return None

        if len(args) > 0:
            if not len(args) == num_args:
                return ValueError

        from typed.mods.types.base import TYPE
        for arg in args:
            if not isinstance(TYPE(arg), base_type):
                raise TypeError(
                    f"Wrong type in polymorphism '{special_method.replace("_", "")}'\n"
                    f" ==> {_name(arg)}: has an unexpected type.\n"
                    f"     [expected_type]: an instance of {_name()}\n"
                    f"     [received_type]: {_name(TYPE(arg))}"
                )

            if not issubclass(TYPE(arg), TYPE(arg[0])):
                raise TypeError(
                    f"Wrong type in polymorphism {special_method.replace("_", "")}\n"
                    f" ==> {_name(arg)}: has an unexpected type.\n"
                    f"     [expected_type]: a subtype of {_name(TYPE(arg[0]))}\n"
                    f"     [received_type]: {_name(TYPE(arg))}"
                )
        try:
            method = getattr(TYPE(args[0]), special_method)
            try:
                return method(*args)
            except Exception as e:
                Exception(e)
        except:
            raise AttributeErr(
                f"Attribute error in {_name(args[0])}:"
                f" ==> its type '{_name(TYPE(args[0]))}' has no attribute '{special_method}'"
            )
    return _poly

join = poly("__join__")
