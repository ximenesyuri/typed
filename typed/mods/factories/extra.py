from functools import lru_cache as cache
from datetime import datetime
from typed.mods.helper.helper import _name

@cache
def Date(date_format):
    from typed.mods.types.base import TYPE, Str
    from typed.mods.types.extra import DateFormat
    if not isinstance(date_format, DateFormat):
        raise TypeError(
            "Date is not in valid format:"
            f" ==> '{date_format}' is not a valid date format string."
            f"      [expected_type] {_name(DateFormat)}"
            f"      [received type] {_name(TYPE(date_format))}"
        )
    class DATE(TYPE(Str)):
        _date_format_str = date_format
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Str):
                return False
            try:
                datetime.strptime(instance, cls._date_format_str).date()
                return True
            except ValueError:
                return False
        def __repr__(self):
            return f"Date('{self._date_format_str}')"
    class_name = f"Date({date_format})"
    return DATE(class_name, (Str,), {
        "__display__": class_name,
        "__null__": "",
    })

@cache
def Time(time_format):
    from typed.mods.types.base import TYPE, Str
    from typed.mods.types.extra import TimeFormat
    if not isinstance(time_format, TimeFormat):
        raise TypeError(
            "Time is not in valid format:"
            f" ==> '{time_format}' is not a valid time format string."
            f"      [expected_type] {_name(TimeFormat)}"
            f"      [received type] {_name(TYPE(time_format))}"
        )

    class TIME(TYPE(Str)):
        _time_format_str = time_format
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Str):
                return False
            try:
                datetime.strptime(instance, cls._time_format_str).time()
                return True
            except ValueError:
                return False

        def __repr__(self):
            return f"Time('{self._time_format_str}')"

    class_name = f"Time({time_format})"
    return TIME(class_name, (Str,), {
        "__display__": class_name,
        "__null__": "",
    })

@cache
def Datetime(datetime_format):
    from typed.mods.types.base import TYPE, Str
    from typed.mods.types.extra import DatetimeFormat
    if not isinstance(datetime_format, DatetimeFormat):
        raise TypeError(
            "Datetime is not in valid format:"
            f" ==> '{datetime_format}' is not a valid datetime format string."
            f"      [expected_type] {_name(DatetimeFormat)}"
            f"      [received type] {_name(TYPE(datetime_format))}"
        )

    class DATETIME(TYPE(Str)):
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
    return DATETIME(class_name, (Str,), {
        "__display__": class_name,
        "__null__": "",
    })
