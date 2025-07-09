from typing import Type
from functools import lru_cache as cache
from datetime import datetime

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
    from typed.mods.types.other import DateFormat
    if not isinstance(date_format, DateFormat):
        raise TypeError(
            f"'{date_format}' is not a valid date format string. "
            f"It must contain standard date formatting directives (e.g., %Y, %m, %d)."
            f" Received type: {type(date_format).__name__}"
        )
    class _Date(type(Str)):
        _date_format_str = date_format
        def __instancecheck__(cls, instance: str) -> bool:
            if not isinstance(instance, Str):
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
    if not isinstance(time_format, TimeFormat):
        raise TypeError(
            f"'{time_format}' is not a valid time format string. "
            f"It must contain standard time formatting directives (e.g., %H, %M, %S)."
            f" Received type: {type(time_format).__name__}"
        )

    class _Time(type(Str)):
        _time_format_str = time_format

        def __instancecheck__(cls, instance: str) -> bool:
            if not isinstance(instance, Str):
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
    if not isinstance(datetime_format, DatetimeFormat):
        raise TypeError(
            f"'{datetime_format}' is not a valid datetime format string. "
            f"It must contain standard date/time formatting directives (e.g., %Y, %m, %d, %H, %M, %S)."
            f" Received type: {type(datetime_format).__name__}"
        )

    class _Datetime(type(Str)):
        _datetime_format_str = datetime_format

        def __instancecheck__(cls, instance: str) -> bool:
            if not isinstance(instance, Str):
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
