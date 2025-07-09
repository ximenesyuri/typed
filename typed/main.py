from typed.mods.helper.helper import _nill, _get_null_object
from typed.mods.types.base          import *
from typed.mods.types.func          import *
from typed.mods.types.attr          import *
from typed.mods.factories.generics  import *
from typed.mods.factories.specifics import *
from typed.mods.factories.base      import *
from typed.mods.factories.func      import *
from typed.mods.decorators          import *

# the null typed function
nill = typed(_nill)

# the null values
null = _get_null_object

