import re
from typing import Type, Tuple as Tuple_
from functools import lru_cache as cache
from datetime import datetime
from typed.mods.types.base import Pattern

@cache
def Extension(ext: str) -> Type:
    from typed.mods.types.base import Path
    class _Extension(type(Path)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Path):
                return False
            parts = instance.split('.')
            return parts[-1] == ext
    return _Extension(f'Extension({ext})', (Path,), {})

@cache
def Date(date_format: datetime) -> Type:
    from typed.mods.factories.generics import Regex
    _DATE_DIRECTIVES = r"(%[YmdjUwWaAbBcxXzZ])"
    _ALLOWED_CHARS = r"(\s|[^%])*"
    DateFormat = Regex(f"^{_ALLOWED_CHARS}({_DATE_DIRECTIVES}{_ALLOWED_CHARS})+$")
    if not isinstance(date_format, DateFormat):
        raise TypeError(
            f"'{date_format}' is not a valid date format string. "
            f"It must contain standard date formatting directives (e.g., %Y, %m, %d)."
            f" Received type: {type(date_format).__name__}"
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

    _Date.__display__ = f"Date('{date_format}')"
    return _Date

@cache
def Time(time_format: datetime) -> Type:
    from typed.mods.factories.generics import Regex
    _TIME_DIRECTIVES = r"(%[HMSfIZp])"
    _ALLOWED_CHARS = r"(\s|[^%])*"
    TimeFormat = Regex(f"^{_ALLOWED_CHARS}({_TIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
    if not isinstance(time_format, TimeFormat):
        raise TypeError(
            f"'{time_format}' is not a valid time format string. "
            f"It must contain standard time formatting directives (e.g., %H, %M, %S)."
            f" Received type: {type(time_format).__name__}"
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

    _Time.__display__ = f"Time('{time_format}')"
    return _Time

@cache
def Datetime(datetime_format: datetime) -> Type:
    from typed.mods.factories.generics import Regex
    _DATETIME_DIRECTIVES = r"(%[YmdHMSfIMjUwWaAbBcxXzZpI])"
    _ALLOWED_CHARS = r"(\s|[^%])*"
    DatetimeFormat = Regex(f"^{_ALLOWED_CHARS}({_DATETIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
    if not isinstance(datetime_format, DatetimeFormat):
        raise TypeError(
            f"'{datetime_format}' is not a valid datetime format string. "
            f"It must contain standard date/time formatting directives (e.g., %Y, %m, %d, %H, %M, %S)."
            f" Received type: {type(datetime_format).__name__}"
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

    _Datetime.__display__ = f"Datetime('{datetime_format}')"
    return _Datetime

@cache
def Url(*protocols: Tuple_[str], pattern: Pattern=None) -> Type:
    from typed.mods.types.base import Protocol
    wrong_type = []
    for prot in protocols:
        if not isinstance(prot, Protocol):
            wrong_type.append(prot)
    if wrong_type:
        message = ""
        for entry in wrong_type:
            message += f"==> '{entry}': is not a valid protocol\n"
            message += f"    [received_type] {type(entry).__name__}\n"
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
                pattern_str = rf"^({str_protocols})(?:[a-z0-9./?#=]+)?$"
                regex = re.compile(pattern_str)
            else:
                pattern_str = rf"^({str_protocols}){pattern.pattern}$"
                regex = re.compile(pattern_str)
            return bool(regex.match(instance))

    return _Url("Url", (str,), {"__display__": f"Url({protocols})"})
