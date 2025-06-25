Int = int
Bool = bool

# -- Simulate decorator
def typed(fn):
    # Sets .domain if not already present
    fn.domain = fn.__annotations__.get('instance', None)
    return fn

# -- Simulate Model
def Model(**kwargs):
    attrs_types = tuple(kwargs.items())
    required_keys = set(kwargs.keys())

    class _Model(type):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, dict):
                return False
            if not required_keys.issubset(instance):
                return False
            for k, t in attrs_types:
                if k in instance and not isinstance(instance[k], t):
                    return False
            return True
    class_name = f"Model({', '.join(f'{k}: {v.__name__}' for k, v in kwargs.items())})"
    return _Model(class_name, (dict,), {})

def Conditional(__conditionals__, __extends__=None, **kwargs):
    # Only use Base if no new fields
    UnderlyingModel = __extends__ if __extends__ and not kwargs else Model(__extends__, **kwargs)
    conds = __conditionals__ if isinstance(__conditionals__, (list, tuple)) else [__conditionals__]
    for cond in conds:
        domain = getattr(cond, 'domain', None)
        if domain is None:
            raise AttributeError("Condition missing domain")
        if not issubclass(UnderlyingModel, domain):
            raise TypeError("Domain does not match underlying model")

    class _Cond(type(UnderlyingModel)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, UnderlyingModel):
                return False
            for cond in conds:
                if not issubclass(UnderlyingModel, cond.domain):
                    return False
            return all(cond(instance) for cond in conds)
    class_name = f"Conditional({UnderlyingModel.__name__})"
    return _Cond(class_name, (UnderlyingModel,), {})

# --- Now try:
model = Model(x=Int)

@typed
def f(instance: model) -> Bool:
    return instance.get('x') > 0

MyModel = Conditional(
    __conditionals__=[f],
    __extends__=model
)

print(isinstance({"x": 2}, MyModel))    # True!
print(isinstance({"x": -1}, MyModel))   # False!
print(isinstance({"x": 2}, model))      # True!
