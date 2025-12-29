from typed.mods.factories.generics import Regex

# Datetime
_DATETIME_DIRECTIVES = r"(%[YmdHMSfIMjUwWaAbBcxXzZpI])"
_DATE_DIRECTIVES = r"(%[YmdjUwWaAbBcxXzZ])"
_TIME_DIRECTIVES = r"(%[HMSfIZp])"
_ALLOWED_CHARS = r"([/\-:\s]|[^%])*"

DatetimeFormat = Regex(f"^{_ALLOWED_CHARS}({_DATETIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
DateFormat = Regex(f"^{_ALLOWED_CHARS}({_DATE_DIRECTIVES}{_ALLOWED_CHARS})+$")
TimeFormat = Regex(f"^{_ALLOWED_CHARS}({_TIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
