from typed.main import *
from typed.models import Model

print(null(Model(x=Str)))
print(Enum(Str, "aa", "bb").__null__)
print(null(Str))
