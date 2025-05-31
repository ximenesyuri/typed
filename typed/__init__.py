from typed.main import *
from typed.models import Instance, Model, ExactModel

json1 = {
    "arg1": "aaa",
    "arg2": 10,
    "arg3": 10,
    "arg4": "aaa"
}

Model1 = Model(
    arg1=Str,
    arg2=Int,
    arg3=Str,
    arg4=Int
)

instance = Model1(json1)

#instance = Instance(entity=json1, model=Model1)

print(issubclass(Model1, Json))
#print(isinstance(instance, Json))

#print(instance.get('arg1'))
