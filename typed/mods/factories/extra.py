import re
from functools import lru_cache as cache
from datetime import datetime
from typed.mods.helper.helper import _name
from typed.mods.helper.null import _null

@cache
def Extension(ext):
    from typed.mods.types.path import Path
    from typed.mods.types.base import TYPE
    class EXTENSION(TYPE(Path)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Path):
                return False
            if instance == '':
                return True
            parts = instance.split('.')
            return parts[-1] == ext
    class_name = f'Extension({ext})'
    return EXTENSION(class_name, (Path,), {
        "__display__": class_name,
        "__null__": _null(Path)
    })

@cache
def Date(date_format):
    from typed.mods.factories.generics import Regex
    from typed.mods.types.base import TYPE, Str
    _DATE_DIRECTIVES = r"(%[YmdjUwWaAbBcxXzZ])"
    _ALLOWED_CHARS = r"(\s|[^%])*"
    DateFormat = Regex(f"^{_ALLOWED_CHARS}({_DATE_DIRECTIVES}{_ALLOWED_CHARS})+$")
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
    from typed.mods.factories.generics import Regex
    from typed.mods.types.base import TYPE, Str
    _TIME_DIRECTIVES = r"(%[HMSfIZp])"
    _ALLOWED_CHARS = r"(\s|[^%])*"
    TimeFormat = Regex(f"^{_ALLOWED_CHARS}({_TIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
    if not isinstance(time_format, TimeFormat):
        raise TypeError(
            "Time is not in valid format:"
            f" ==> '{date_format}' is not a valid time format string."
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
    from typed.mods.factories.generics import Regex
    from typed.mods.types.base import TYPE, Str
    _DATETIME_DIRECTIVES = r"(%[YmdHMSfIMjUwWaAbBcxXzZpI])"
    _ALLOWED_CHARS = r"(\s|[^%])*"
    DatetimeFormat = Regex(f"^{_ALLOWED_CHARS}({_DATETIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
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

@cache
def Url(*protocols, pattern=None):
    from typed.mods.types.extra import Protocol
    from typed.mods.types.base import TYPE, Str
    wrong_type = []
    for prot in protocols:
        if not isinstance(prot, Protocol):
            wrong_type.append(prot)
    if wrong_type:
        message = ""
        for entry in wrong_type:
            message += f"==> '{entry}': is not a valid protocol\n"
            message += f"    [received_type] {_name(TYPE(entry))}\n"
            message += f"    [expected_type] Protocol\n"
        raise TypeError(
            f"There are entries which are not valid protocols.\n" + message
        )

    class URL(TYPE(Str)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, Str):
                return False

            full_protocols = [f"{prot}://" for prot in protocols]
            str_protocols = "|".join(map(re.escape, full_protocols))
            if not pattern:
                pattern_str = rf"^({str_protocols})\S+$"
                regex = re.compile(pattern_str)
            else:
                pattern_str = rf"^({str_protocols}){pattern.pattern}$"
                regex = re.compile(pattern_str)
            return bool(regex.match(instance))

    class_name = f"Url{protocols}"
    return URL("Url", (Str,), {
        "__display__": class_name,
        "__null__": ""
    })
