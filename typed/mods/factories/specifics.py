import re
from typing import Type, Tuple as Tuple_
from functools import lru_cache as cache
from datetime import datetime
from typed.mods.types.base import Pattern
from typed.mods.helper.helper import _name
from typed.mods.helper.null import _null

@cache
def Extension(ext: str) -> Type:
    from typed.mods.types.base import Path
    class _Extension(type(Path)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Path):
                return False
            parts = instance.split('.')
            return parts[-1] == ext
    class_name = f'Extension({ext})'
    return _Extension(class_name, (Path,), {
        "__display__": class_name,
        "__null__": _null(Path)
    })

@cache
def Date(date_format: datetime) -> Type:
    from typed.mods.factories.generics import Regex
    _DATE_DIRECTIVES = r"(%[YmdjUwWaAbBcxXzZ])"
    _ALLOWED_CHARS = r"(\s|[^%])*"
    DateFormat = Regex(f"^{_ALLOWED_CHARS}({_DATE_DIRECTIVES}{_ALLOWED_CHARS})+$")
    if not isinstance(date_format, DateFormat):
        raise TypeError(
            "Date is not in valid format:"
            f" ==> '{date_format}' is not a valid date format string."
            f"      [expected_type] {_name(DateFormat)}"
            f"      [received type] {_name(type(date_format))}"
        )
    class _Date(type(str)):
        _date_format_str = date_format
        def __instancecheck__(cls, instance):
            if not isinstance(instance, str):
                return False
            try:
                datetime.strptime(instance, cls._date_format_str).date()
                return True
            except ValueError:
                return False
        def __repr__(self):
            return f"Date('{self._date_format_str}')"
    class_name = f"Date({date_format})"
    return _Date(class_name, (str,), {
        "__display__": class_name,
        "__null__": "",
    })

@cache
def Time(time_format: datetime) -> Type:
    from typed.mods.factories.generics import Regex
    _TIME_DIRECTIVES = r"(%[HMSfIZp])"
    _ALLOWED_CHARS = r"(\s|[^%])*"
    TimeFormat = Regex(f"^{_ALLOWED_CHARS}({_TIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
    if not isinstance(time_format, TimeFormat):
        raise TypeError(
            "Time is not in valid format:"
            f" ==> '{date_format}' is not a valid time format string."
            f"      [expected_type] {_name(TimeFormat)}"
            f"      [received type] {_name(type(time_format))}"
        )

    class _Time(type(str)):
        _time_format_str = time_format
        def __instancecheck__(cls, instance):
            if not isinstance(instance, str):
                return False
            try:
                datetime.strptime(instance, cls._time_format_str).time()
                return True
            except ValueError:
                return False

        def __repr__(self):
            return f"Time('{self._time_format_str}')"

    class_name = f"Time({time_format})"
    return _Time(class_name, (str,), {
        "__display__": class_name,
        "__null__": "",
    })

@cache
def Datetime(datetime_format: datetime) -> Type:
    from typed.mods.factories.generics import Regex
    _DATETIME_DIRECTIVES = r"(%[YmdHMSfIMjUwWaAbBcxXzZpI])"
    _ALLOWED_CHARS = r"(\s|[^%])*"
    DatetimeFormat = Regex(f"^{_ALLOWED_CHARS}({_DATETIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
    if not isinstance(datetime_format, DatetimeFormat):
        raise TypeError(
            "Datetime is not in valid format:"
            f" ==> '{datetime_format}' is not a valid datetime format string."
            f"      [expected_type] {_name(DatetimeFormat)}"
            f"      [received type] {_name(type(datetime_format))}"
        )

    class _Datetime(type(str)):
        _datetime_format_str = datetime_format

        def __instancecheck__(cls, instance):
            if not isinstance(instance, str):
                return False
            try:
                datetime.datetime.strptime(instance, cls._datetime_format_str)
                return True
            except ValueError:
                return False

        def __repr__(self):
            return f"Datetime('{self._datetime_format_str}')"

    class_name = f"Datetime({datetime_format})"
    return _Datetime(class_name, (str,), {
        "__display__": class_name,
        "__null__": "",
    })

@cache
def Url(*protocols: Tuple_[str], pattern: Pattern=None) -> Type:
    from typed.mods.types.other import Protocol
    wrong_type = []
    for prot in protocols:
        if not isinstance(prot, Protocol):
            wrong_type.append(prot)
    if wrong_type:
        message = ""
        for entry in wrong_type:
            message += f"==> '{entry}': is not a valid protocol\n"
            message += f"    [received_type] {_name(type(entry))}\n"
            message += f"    [expected_type] Protocol\n"
        raise TypeError(
            f"There are entries which are not valid protocols.\n" + message
        )

    class _Url(type(str)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, str):
                return False

            full_protocols = [f"{prot}://" for prot in protocols]
            str_protocols = "|".join(map(re.escape, full_protocols))
            if not pattern:
                pattern_str = rf"^({str_protocols})(?:[a-z0-9./?#=@:]+)?$"
                regex = re.compile(pattern_str)
            else:
                pattern_str = rf"^({str_protocols}){pattern.pattern}$"
                regex = re.compile(pattern_str)
            return bool(regex.match(instance))

    class_name = f"Url({protocols})"
    return _Url("Url", (str,), {
        "__display__": class_name,
        "__null__": ""
    })
