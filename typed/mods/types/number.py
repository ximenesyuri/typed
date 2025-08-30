from typed.mods.factories.base     import Union
from typed.mods.factories.generics import Filter
from typed.mods.decorators         import typed
from typed.mods.types.base         import Int, Float, Bool

Num = Union(Int, Float)

def _is_natural(x: Int) -> Bool:
    return x >= 0

def _is_odd(x: Int) -> Bool:
  return x % 2 != 0

def _is_even(x: Int) -> Bool:
  return x % 2 == 0

def _is_positive_int(x: Int) -> Bool:
    return x > 0

def _is_negative_int(x: Int) -> Bool:
    return x < 0

def _is_positive_num(x: Num) -> Bool:
    return x > 0

def _is_negative_num(x: Num) -> Bool:
    return x < 0

Nat    = Filter(Int, typed(_is_natural))
Odd    = Filter(Int, typed(_is_odd))
Even   = Filter(Int, typed(_is_even))
Pos    = Filter(Int, typed(_is_positive_int))
Neg    = Filter(Int, typed(_is_negative_int))
PosNum = Filter(Num, typed(_is_positive_num))
NegNum = Filter(Num, typed(_is_negative_num))

Num.__display__    = "Num"
Nat.__display__    = "Nat"
Odd.__display__    = "Odd"
Even.__display__   = "Even"
Pos.__display__    = "Pos"
Neg.__display__    = "Neg"
PosNum.__display__ = "PosNum"
NegNum.__display__ = "NegNum"

Num.__null__    = 0.0
Nat.__null__    = 0
Odd.__null__    = None
Even.__null__   = 0
Pos.__null__    = None
Neg.__null__    = None
PosNum.__null__ = None
NegNum.__null__ = None
