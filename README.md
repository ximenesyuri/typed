```ruby
   /00                                         /00
  | 00                                        | 00
 /000000   /00   /00  /000000   /000000   /0000000
|_  00_/  | 00  | 00 /00__  00 /00__  00 /00__  00
  | 00    | 00  | 00| 00  \ 00| 00000000| 00  | 00
  | 00 /00| 00  | 00| 00  | 00| 00_____/| 00  | 00
  |  0000/|  0000000| 0000000/|  0000000|  0000000
   \___/   \____  00| 00____/  \_______/ \_______/
           /00  | 00| 00|                          
          |  000000/| 00|                          
           \______/ |__/
```

# About

`typed` is a Python framework providing type safety and allowing universal constructions.

# Overview

The lib provides a lot of `type factories`, which can be used to build custom types, which are **subtypes** of already existing types. This means that initalization is not needed during the runtime type checking. The lib also provides a class of `typed functions`, for which type hints are checked at runtime. 

So, with `typed` you have a framework ensuring type safety by:
1. defining custom types from `type factories`
2. using those custom types as type hints for `typed functions`
3. checking the type hints at runtime.

> `typed` includes a lot ready to use classes from different contexts.
    
You can also use `typed` to create and validate data models similar to [pydantic](https://github.com/pydantic/pydantic). 

# Install

With `pip`:
```bash
pip install git+https://github.com/pythonalta/typed  
``` 

With [py](https://github.com/ximenesyuri/py)
```bash
py i pythonalta/typed  
```

# Basic Usage
 
Just use custom types created from `type factories` as type hints for `typed functions`, which are created with the `typed` decorator.

```python
# import 'typed' decorator 
from typed import typed
# import some 'type factories'
from typed import List, Int, Str

# then define a 'typed function'
@typed
def my_function(x: Int, y: Str) -> List(Int, Str):
    return [x, y]
```

If at runtime the type of `x` does not matches `Int` (respectively the type of `y` does not matches `Str` or the return type of `my_function` does not matches `List(Int, Str)`), then a descriptive `Type Error` message is provided, presenting the received types and the expected types.

# Models

You can create `type models` which are subclasses of the base `Json` class and can be used to quickly validate data, as you can do with `BaseModel` in [pydantic](https://github.com/pydantic/pydantic):

```python
from typed        import Int, Str, List
from typed.models import Model

Model1 = Model(
    arg1=Str,
    arg2=Int,
    arg3=List(Int, Str)
)

json1 = {
    'arg1': 'foo',
    'arg2': 'bar',
    'arg3': [1, 'foobar']
}
```

With the above, `isinstance(json1, Model1)` returns `False`, since `arg2` is expected to be an integer. As a consequence, if you use that in a `typed function`, this will raise a `TypeError`:

```python
from typed import typed
from some.where import Model1

@typed
def some_function(some_json: Model1) -> Model1:
    ...
    return some_json

some_function(json1) # a raise descriptive TypeError
```

# Validation

You can validade a model entity before calling it in a typed function using the `Instance` checker:

```python
from typed        import typed, Int, Str, List
from typed.models import Model, Instance

Model1 = Model(
    arg1=Str,
    arg2=Int,
    arg3=List(Int, Str)
)

json1 = {
    'arg1': 'foo',
    'arg2': 'bar',
    'arg3': [1, 'foobar']
}

model1_instance = Instance(
    model=Model1,
    entity=json1
)
```

> Such a validation is better than using just `isinstance(entity, model)` because it parses the `entity` and provides specific errors, while `isinstance` just return a boolean value.

Another way to validate an instance is to call it directly as an argument for some `model`:
```python
model1_instance = Model1({
    'arg1': 'foo',
    'arg2': 'bar',
    'arg3': [1, 'foobar']
})
```

You can also use a `kwargs` approach:

```python
model1_instance = Model1({
    arg1='foo',
    arg2='bar',
    arg3=[1, 'foobar']
})
```

> Notice that you can also use the above approaches to **create** valid instances and not only to validate **already existing** instances.


# Exact Models

In [pydantic](https://github.com/pydantic/pydantic), a model created from `BaseModel` do a strict validation: a json data is considered an instance of the model iff it exactly matches the non-optional entries.  In `typed` , the `Model` factory creates subtypes of `Json`, so that a typical type checking will only evaluate if a json data **contains** the data defined in the model obtained from `Model`. So, for example, the following will not raise a `TypeError`:

```python
from typed        import typed, Int, Str, List
from typed.models import Model, Instance

Model1 = Model(
    arg1=Str,
    arg2=Int,
    arg3=List(Int, Str)
)

json2 = {
    'arg1': 'foo',
    'arg2': 2,
    'arg3': [1, 'foobar']
    'arg4': 'bar'
}

model1_instance = Instance(
    model=Model1,
    entity=json2
)
```

For an exact evaluation, as occurs while using `BaseModel`, you could use the `Exact` factory from `typed.models`. It also provides a `Optional` directive, as in [pydantic](https://github.com/pydantic/pydantic):

```python
from typed        import typed, Int, Str, List
from typed.models import ExactModel, Instance

Model1 = ExactModel(
    arg1=Str,
    arg2=Optional(Int, 0),  # optional entries always expect a default value
    arg3=List(Int, Str)
)

Model2 = ExactModel(
    arg1=Str,
    arg2=Int,
    arg3=List(Int, Str)
)

json1 = {
    'arg1': 'foo',
    'arg3': [1, 'foobar']
}

json2 = {
    'arg1': 'foo',
    'arg2': 2,
    'arg3': [1, 'foobar']
}

# will NOT raise a TypeError
model1_instance = Instance(
    model=Model1,
    entity=json1
)

# will NOT raise a TypeError
model2_instance = Instance(
    model=Model2,
    entity=json2
)

# WILL raise a TypeError
model2_instance = Instance(
    model=Model2,
    entity=json1
)
```

# Primitive Types

The following  is the list of the primitive `typed` types, from which, using `type factories`, one can build other derived types.

```
primitive Python types
------------------------
type        definition 
--------------------------------------------- 
Int         int
Str         str
Bool        bool
Float       float
Nill        type(None)
```

```
additional typed types
--------------------------
type         definition 
---------------------------------------------
Any          isinstance(x, Any) is True everywhere
Path         Union(Regex(...), Null(Str))
Pattern      isinstance(x, Patter) is True if x is r"..."
Json         Union(Dict(Any), List(Any), Set(Any))
```

```
function types
---------------------------
type           definition
---------------------------------------------
PlainFuncType  ...
HintedFuncType
TypedFuncType
```

# Factories


# Derived Types

```
typed.examples
```

# Use Cases
