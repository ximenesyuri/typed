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

The framework provides a lot of _primitive types_ with a plethora of _type factories_, which can be used to build custom _derived types_. As examples of the type factories we have _type operations_, which concretely implements the annotations from the `typing` library, and flavors of _models_, which can be used to validate data. 

One time defined, the types can be used as type hints for _typed functions_, for which type hints are checked at runtime. 

So, with `typed` you have a framework ensuring type safety by:
1. defining custom types from _type factories_;
2. using those custom types as type hints for _typed functions_;
3. checking the type hints at runtime.


# Install

With `pip`:
```bash
pip install git+https://github.com/ximenesyuri/typed  
``` 

With [py](https://github.com/ximenesyuri/py)
```bash
py i ximenesyuri/typed  
```

# Documentation

Please, see [ximenesyuri.com/libs/typed](https://ximenesyuri.com/libs/typed).


