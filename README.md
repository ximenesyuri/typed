# About

`typed` is lightweight runtime type checking solution for Python. Zero dependencies. No need of prebuild steps, static analysis, IDE plugins, and so on.

# Overview

The lib provides a lot of `type factories`, which can be used to build custom types, which are **subtypes** of already existing types. This means that initalization is not needed during the runtime type checking. The lib also provides a class of `typed functions`, for which type hints are checked at runtime. 

So, with `typed` you have a framework ensuring type safety by:
1. defining custom types from `type factories`
2. using those custom types as type hints for `typed functions`
3. checking the type hints at runtime.

The lib includes a lot ready to use classes from different contexts.

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

You can create `type models` which are subclasses of the base `Json` class and can be used to quickly validate data, as you did with `BaseModels` in [pydantic](https://github.com/pydantic/pydantic):

```python
from typed import typed
from typed import Model, Int, Str, List

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

With the above, `isinstance(json1, Model1)` returns `False`. As a consequence, if you use that in a `typed function`, this will raise a `TypeError`:

```python
@typed
def some_function(some_json: Model1) -> Model1:
    ...
    return some_json

some_function(json1) # raise descriptive TypeError
```

# See Also

For more details, see [ximenesyuri.com/dev/typed](https://ximenesyuri.com/dev/typed).
