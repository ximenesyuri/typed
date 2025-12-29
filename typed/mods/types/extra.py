from typed.mods.types.base         import Str, Bool
from typed.mods.factories.generics import Regex, Filter
from typed.mods.decorators         import typed

# Network

IPv4     = Regex(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

@typed
def _is_ipv6(string: Str) -> Bool:
    from ipaddress import IPv6Address
    try:
        IPv6Address(string)
        return True
    except:
        return False

IPv6 = Filter(Str, _is_ipv6)

IPv4.__display__     = "IPv4"

# IDs
UUID = Regex(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
UUID.__display__ = "UUID"

# Datetime
_DATETIME_DIRECTIVES = r"(%[YmdHMSfIMjUwWaAbBcxXzZpI])"
_DATE_DIRECTIVES = r"(%[YmdjUwWaAbBcxXzZ])"
_TIME_DIRECTIVES = r"(%[HMSfIZp])"
_ALLOWED_CHARS = r"([/\-:\s]|[^%])*"

DatetimeFormat = Regex(f"^{_ALLOWED_CHARS}({_DATETIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
DateFormat = Regex(f"^{_ALLOWED_CHARS}({_DATE_DIRECTIVES}{_ALLOWED_CHARS})+$")
TimeFormat = Regex(f"^{_ALLOWED_CHARS}({_TIME_DIRECTIVES}{_ALLOWED_CHARS})+$")
