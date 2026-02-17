import inspect

class _Placeholder:
    def __init__(self, base, transform):
        self.base = base
        self.transform = transform

    def _get_value(self, args, kwargs):
        value = self.base._get_value(args, kwargs)
        return self.transform(value) if value is not None else None

    def __eq__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val == other_val
        return predicate

    def __lt__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val < other_val
        return predicate

    def __gt__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val > other_val
        return predicate

    def __le__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val <= other_val
        return predicate

    def __ge__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val >= other_val
        return predicate

    def __ne__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val != other_val
        return predicate

    # --- Arithmetic operators (optional but usually handy) ---
    def __add__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val + other_val
        return func

    def __radd__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return other_val + self_val
        return func

    def __sub__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val - other_val
        return func

    def __rsub__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return other_val - self_val
        return func

    def __mul__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val * other_val
        return func

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val / other_val
        return func

    def __rtruediv__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return other_val / self_val
        return func

    def __floordiv__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val // other_val
        return func

    def __mod__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val % other_val
        return func

    def __pow__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val ** other_val
        return func


class Placeholder:
    _cache = {}

    def __new__(cls, index):
        if index not in cls._cache:
            instance = super().__new__(cls)
            instance.index = index
            cls._cache[index] = instance
        return cls._cache[index]

    def __repr__(self):
        return f"_{self.index}" if self.index > 0 else "_"

    def __str__(self):
        return f"_{self.index}" if self.index > 0 else "_"

    def _get_value(self, args, kwargs):
        if self.index <= 0:
            return None
        if self.index <= len(args):
            return args[self.index - 1]
        kwarg_keys = list(kwargs.keys())
        if self.index <= len(args) + len(kwarg_keys):
            return kwargs[kwarg_keys[self.index - len(args) - 1]]
        return None

    def len(self):
        return _Placeholder(self, lambda v: len(v))

    def int(self):
        return _Placeholder(self, lambda v: int(v))

    def float(self):
        return _Placeholder(self, lambda v: float(v))

    def bool(self):
        return _Placeholder(self, lambda v: bool(v))

    def str(self):
        return _Placeholder(self, lambda v: str(v))

    def repr(self):
        return _Placeholder(self, lambda v: repr(v))

    def __eq__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val == other_val
        return predicate

    def __lt__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val < other_val
        return predicate

    def __gt__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val > other_val
        return predicate

    def __le__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val <= other_val
        return predicate

    def __ge__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val >= other_val
        return predicate

    def __ne__(self, other):
        def predicate(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            return self_val != other_val
        return predicate

    def __add__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val + other_val
        return func

    def __radd__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return other_val + self_val
        return func

    def __sub__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val - other_val
        return func

    def __rsub__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return other_val - self_val
        return func

    def __mul__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val * other_val
        return func

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val / other_val
        return func

    def __rtruediv__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return other_val / self_val
        return func

    def __floordiv__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val // other_val
        return func

    def __mod__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val % other_val
        return func

    def __pow__(self, other):
        def func(*args, **kwargs):
            self_val = self._get_value(args, kwargs)
            if isinstance(other, (Placeholder, _Placeholder)):
                other_val = other._get_value(args, kwargs)
            else:
                other_val = other
            if self_val is None or other_val is None:
                return None
            return self_val ** other_val
        return func

    def __getattr__(self, name):
        if name == "append":
            def append_caller(*args, **kwargs):
                def func(*call_args, **call_kwargs):
                    obj = self._get_value(call_args, call_kwargs)
                    if obj is None:
                        return None

                    resolved_args = [
                        _resolve_placeholder_value(a, call_args, call_kwargs)
                        for a in args
                    ]

                    resolved_kwargs = {
                        k: _resolve_placeholder_value(v, call_args, call_kwargs)
                        for k, v in kwargs.items()
                    }

                    return _append(obj, *resolved_args, **resolved_kwargs)

                return func
            return append_caller

        if name == "join":
            def join_caller(*args, **kwargs):
                if kwargs:
                    raise TypeError("Placeholder.join does not support keyword arguments")

                def func(*call_args, **call_kwargs):
                    obj = self._get_value(call_args, call_kwargs)
                    if obj is None:
                        return None

                    resolved_args = [
                        _resolve_placeholder_value(a, call_args, call_kwargs)
                        for a in args
                    ]

                    return _join(obj, *resolved_args)

                return func
            return join_caller

        if name == "split":
            def split_caller(*args, **kwargs):
                def func(*call_args, **call_kwargs):
                    obj = self._get_value(call_args, call_kwargs)
                    if obj is None:
                        return None

                    resolved_args = [
                        _resolve_placeholder_value(a, call_args, call_kwargs)
                        for a in args
                    ]

                    resolved_kwargs = {
                        k: _resolve_placeholder_value(v, call_args, call_kwargs)
                        for k, v in kwargs.items()
                    }

                    return _split(obj, *resolved_args, **resolved_kwargs)

                return func
            return split_caller

        def method_caller(*args, **kwargs):
            def func(*call_args, **call_kwargs):
                obj = self._get_value(call_args, call_kwargs)
                if obj is None:
                    return None
                method = getattr(obj, name)

                resolved_args = []
                for a in args:
                    if isinstance(a, (Placeholder, _Placeholder)):
                        resolved_args.append(a._get_value(call_args, call_kwargs))
                    elif callable(a):
                        sig = inspect.signature(a)
                        params = list(sig.parameters.values())
                        has_var = any(
                            p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
                            for p in params
                        )
                        pos = [
                            p for p in params
                            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                        ]
                        if has_var or len(pos) == 0:
                            resolved_args.append(a(*call_args, **call_kwargs))
                        else:
                            resolved_args.append(a)
                    else:
                        resolved_args.append(a)

                resolved_kwargs = {}
                for k, v in kwargs.items():
                    if isinstance(v, (Placeholder, _Placeholder)):
                        resolved_kwargs[k] = v._get_value(call_args, call_kwargs)
                    elif callable(v):
                        sig = inspect.signature(v)
                        params = list(sig.parameters.values())
                        has_var = any(
                            p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
                            for p in params
                        )
                        pos = [
                            p for p in params
                            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                        ]
                        if has_var or len(pos) == 0:
                            resolved_kwargs[k] = v(*call_args, **call_kwargs)
                        else:
                            resolved_kwargs[k] = v
                    else:
                        resolved_kwargs[k] = v

                return method(*resolved_args, **resolved_kwargs)

            return func

        return method_caller

class Var:
    def __init__(self):
        self._placeholder_cache = {}
        self._name_to_index = {}
        self._next_index = 1

    def __repr__(self):
        return "var"

    def __call__(self, key):
        if isinstance(key, int) and key > 0:
            if key not in self._placeholder_cache:
                self._placeholder_cache[key] = Placeholder(key)
                self._next_index = max(self._next_index, key + 1)
            return self._placeholder_cache[key]

        if isinstance(key, str):
            idx = self._name_to_index.get(key)
            if idx is None:
                idx = self._next_index
                self._next_index += 1
                self._name_to_index[key] = idx
            if idx not in self._placeholder_cache:
                self._placeholder_cache[idx] = Placeholder(idx)
            return self._placeholder_cache[idx]

        raise TypeError("var(key): key must be a positive int or a string")

    def __getattr__(self, name):
        if name.startswith('_') and name[1:].isdigit():
            index = int(name[1:])
            if index <= 0:
                raise AttributeError(f"'var' object has no attribute '{name}'")
            return self(index)

        if name.isidentifier():
            return self(name)

        raise AttributeError(f"'var' object has no attribute '{name}'")

def _is_placeholder_like(x):
    if isinstance(x, (Placeholder, _Placeholder)):
        return True
    if callable(x):
        sig = inspect.signature(x)
        params = list(sig.parameters.values())
        has_var = any(
            p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
            for p in params
        )
        pos = [
            p for p in params
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        return has_var or len(pos) == 0
    return False


def _resolve_placeholder_value(val, call_args, call_kwargs):
    if isinstance(val, (Placeholder, _Placeholder)):
        return val._get_value(call_args, call_kwargs)
    if callable(val):
        sig = inspect.signature(val)
        params = list(sig.parameters.values())
        has_var = any(
            p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
            for p in params
        )
        pos = [
            p for p in params
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        if has_var or len(pos) == 0:
            return val(*call_args, **call_kwargs)
    return val


def _append(obj, *args, **kwargs):
    if isinstance(obj, dict):
        if args:
            if len(args) == 1 and isinstance(args[0], dict):
                obj.update(args[0])
            else:
                for k, v in args:
                    obj[k] = v
        if kwargs:
            obj.update(kwargs)
        return obj

    if isinstance(obj, set):
        for v in args:
            obj.add(v)
        return obj

    if hasattr(obj, "__append__"):
        result = obj.__append__(*args, **kwargs)
        return obj if result is None else result

    if hasattr(obj, "append"):
        for v in args:
            obj.append(v)
        return obj

    raise TypeError(
        f"append(): object of type {type(obj)!r} does not support "
        "append/add/update/__append__"
    )

def _join_dicts(*dicts, on_conflict="error"):
    result = {}
    for d in dicts:
        for k, v in d.items():
            if k not in result:
                result[k] = v
            else:
                if on_conflict == "error":
                    raise KeyError(f"duplicate key {k!r}")
                elif on_conflict == "first":
                    continue
                elif on_conflict == "last":
                    result[k] = v
                elif callable(on_conflict):
                    result[k] = on_conflict(k, result[k], v)
                else:
                    raise ValueError(f"Unknown on_conflict={on_conflict!r}")
    return result


def _join(*args, on_conflict="error"):
    if not args:
        return []

    if len(args) == 2:
        a, b = args
        if isinstance(a, str) and isinstance(b, (list, tuple)):
            return a.join(b)
        if isinstance(b, str) and isinstance(a, (list, tuple)):
            return b.join(a)

    if all(isinstance(a, str) for a in args):
        return "".join(args)

    if all(isinstance(a, dict) for a in args):
        return _join_dicts(*args, on_conflict=on_conflict)

    if all(isinstance(a, set) for a in args):
        result = set()
        for s in args:
            result |= s
        return result

    if all(isinstance(a, list) for a in args):
        result = []
        for lst in args:
            result.extend(lst)
        return result

    first = args[0]
    t = type(first)
    if hasattr(t, "__join__"):
        return getattr(t, "__join__")(*args)

    raise TypeError(
        "join(): unsupported argument combination:\n"
        f"  types = {[type(a) for a in args]!r}"
    )

def _split(obj, *, by=None, size=None, key=None, predicate=None):
    if isinstance(obj, str):
        if by is not None and size is not None:
            raise ValueError("split(str): specify either 'by' or 'size', not both")
        if by is not None:
            return obj.split(by)
        if size is not None:
            if size <= 0:
                raise ValueError("split(str): 'size' must be positive")
            return [obj[i : i + size] for i in range(0, len(obj), size)]
        return obj.split()

    if isinstance(obj, (list, tuple)):
        seq = list(obj)

        if size is not None:
            if size <= 0:
                raise ValueError("split(seq): 'size' must be positive")
            chunks = [seq[i : i + size] for i in range(0, len(seq), size)]
            return [type(obj)(chunk) for chunk in chunks]

        if predicate is not None:
            left = [x for x in seq if predicate(x)]
            right = [x for x in seq if not predicate(x)]
            return [type(obj)(left), type(obj)(right)]

        if key is not None:
            groups = {}
            for x in seq:
                k = key(x)
                groups.setdefault(k, []).append(x)
            return {k: type(obj)(v) for k, v in groups.items()}

        raise ValueError(
            "split(seq): must specify at least one of 'size', 'predicate', or 'key'"
        )

    if isinstance(obj, dict):
        if by is not None and not isinstance(by, (set, list, tuple)):
            raise TypeError("split(dict): 'by' must be an iterable of keys")

        if by is not None:
            keyset = set(by)
            left = {k: v for k, v in obj.items() if k in keyset}
            right = {k: v for k, v in obj.items() if k not in keyset}
            return [left, right]

        if predicate is not None:
            left = {}
            right = {}
            for k, v in obj.items():
                if predicate(k, v):
                    left[k] = v
                else:
                    right[k] = v
            return [left, right]

        if key is not None:
            groups = {}
            for k, v in obj.items():
                g = key(k, v)
                groups.setdefault(g, {})[k] = v
            return groups

        raise ValueError(
            "split(dict): must specify one of 'by', 'predicate', or 'key'"
        )

    t = type(obj)
    if hasattr(t, "__split__"):
        return getattr(t, "__split__")(obj, by=by, size=size, key=key, predicate=predicate)

    raise TypeError(f"split(): unsupported object type {type(obj)!r}")

class Switch:
    def __init__(self, *, value):
        self.default_value = value
        self._model_cases = []
        self._cond_cases = []
        self._plain_cases = []
        self._built = None

    def case(self, value, when):
        from typed.mods.types.func import Condition, Typed
        from typed.mods.types.base import Bool
        from typed.mods.helper.models import Expr
        from typed.mods.helper.helper import _name

        if isinstance(when, Expr):
            self._model_cases.append((value, when))
            return self

        if isinstance(when, bool):
            self._model_cases.append((value, when))
            self._plain_cases.append((value, (lambda: when)))
            return self

        if isinstance(when, Condition):
            if when.cod is not Bool:
                raise TypeError(
                    "Wrong codomain in switch condition:\n"
                    f" ==> '{_name(when)}' does not return Bool\n"
                    "     [expected_type] Bool\n"
                    f"     [received_type] '{_name(when.cod)}'"
                )
            self._cond_cases.append((value, when))
            return self

        if callable(when):
            sig = inspect.signature(when)
            num_params = len(sig.parameters)
            is_lambda = inspect.isfunction(when) and when.__name__ == "<lambda>"

            if is_lambda and num_params == 0:
                self._model_cases.append((value, when))
                self._plain_cases.append((value, when))
                return self

            if is_lambda:
                self._plain_cases.append((value, when))
                return self

            try:
                typed_cond = Typed(when)
            except Exception:
                raise

            if typed_cond.codomain is not Bool:
                raise TypeError(
                    "Wrong codomain in switch condition:\n"
                    f" ==> '{_name(when)}' does not return Bool\n"
                    "     [expected_type] Bool\n"
                    f"     [received_type] '{_name(typed_cond.codomain)}'"
                )

            self._cond_cases.append((value, typed_cond))
            return self

        raise TypeError(
            "Switch.case(value, when): 'when' must be one of:\n"
            "  - Bool\n"
            "  - lambda (with 0 or more parameters)\n"
            "  - function with type hints returning Bool\n"
            "  - Expr (in model defaults)\n"
            f"     [received_type] {type(when)}"
        )

    def _eval_model_condition(self, cond):
        from typed.mods.helper.models import Expr

        if isinstance(cond, Expr):
            return bool(cond())

        if isinstance(cond, bool):
            return cond

        if callable(cond):
            v = cond()
            if isinstance(v, Expr):
                return bool(v())
            return bool(v)

        return bool(cond)

    def evaluate(self):
        if not self._model_cases:
            dv = self.default_value
            return dv() if callable(dv) else dv

        for val, cond in self._model_cases:
            if self._eval_model_condition(cond):
                return val() if callable(val) else val

        dv = self.default_value
        return dv() if callable(dv) else dv

    def check_type(self, typ):
        from typed.mods.types.base import TYPE
        if not isinstance(typ, TYPE):
            return False

        from typed.mods.helper.models import Expr

        def _value_ok(v):
            if v is None:
                return True
            if isinstance(v, Expr):
                return True
            if callable(v):
                return True
            try:
                return v in typ
            except Exception:
                return True

        if not _value_ok(self.default_value):
            return False
        for v, _cond in self._model_cases:
            if not _value_ok(v):
                return False
        return True

    def _condition_domain(self):
        if not self._cond_cases:
            return ()
        dom0 = self._cond_cases[0][1].domain
        for _v, cond in self._cond_cases[1:]:
            if cond.domain != dom0:
                from typed.mods.helper.helper import _name
                raise TypeError(
                    "All typed branches in switch() must have the same domain.\n"
                    f" ==> first domain: {dom0}\n"
                    f"     found:        {cond.domain} in '{_name(cond)}'"
                )
        return dom0

    def _condition_codomain(self):
        from typed.mods.types.base import TYPE as TYPE_BASE
        from typed.mods.factories.base import Union
        types = []
        if self.default_value is not None:
            types.append(TYPE_BASE(self.default_value))
        for v, _ in self._cond_cases:
            if v is not None:
                types.append(TYPE_BASE(v))
        if not types:
            from typed.mods.types.base import Any
            return Any
        return Union(*types)

    def _build_typed_function(self):
        from typing import get_type_hints
        from typed.mods.decorators import typed

        if not self._cond_cases:
            dv = self.default_value
            return dv() if callable(dv) else dv

        first_value, first_cond = self._cond_cases[0]
        orig_func = getattr(first_cond, "func", first_cond)

        sig = inspect.signature(orig_func)
        type_hints = get_type_hints(orig_func)

        codomain = self._condition_codomain()

        impl_annotations = {}
        for name, param in sig.parameters.items():
            if name in type_hints:
                impl_annotations[name] = type_hints[name]
        impl_annotations["return"] = codomain

        self._condition_domain()

        def _impl(*args, **kwargs):
            for v, cond in self._cond_cases:
                if cond(*args, **kwargs):
                    return v
            return self.default_value

        _impl.__name__ = "switch_result"
        _impl.__annotations__ = impl_annotations

        return typed(_impl)

    def _build_plain(self):
        if not self._plain_cases:
            dv = self.default_value
            return dv() if callable(dv) else dv

        import inspect
        _, first_pred = self._plain_cases[0]
        sig = inspect.signature(first_pred)
        num_params = len(sig.parameters)

        if num_params == 0:
            for v, pred in self._plain_cases:
                if pred():
                    return v
            return self.default_value

        def _impl(*args, **kwargs):
            for v, pred in self._plain_cases:
                if pred(*args, **kwargs):
                    return v
            return self.default_value

        _impl.__name__ = "switch_result"
        return _impl

    def end(self):
        if self._built is not None:
            return self._built

        if self._cond_cases and self._plain_cases:
            raise TypeError(
                "Cannot mix typed (Condition/Typed Bool) and plain (lambda) "
                "conditions in the same switch()."
            )

        if self._cond_cases:
            dom = self._condition_domain()
            if len(dom) == 0:
                for v, cond in self._cond_cases:
                    if cond():
                        self._built = v
                        break
                else:
                    self._built = self.default_value
            else:
                self._built = self._build_typed_function()

        elif self._plain_cases:
            self._built = self._build_plain()

        else:
            self._built = self

        return self._built

class Func:
    def __init__(self, *iterables, **param_types):
        self._loops = []
        for it in iterables:
            self._add_loop(it, stop=None)

        self._param_types = dict(param_types)

        from typed.mods.general import var as _var
        _var._placeholder_cache.clear()
        _var._name_to_index.clear()
        _var._next_index = 1
        for name in self._param_types.keys():
            _var(name)

        self._predicate = None
        self._pred_arity = 0
        self._pred_variadic = False

        self._mode = "simple"
        self._cases = []
        self._pending_case_pred = None
        self._pending_case_arity = 0
        self._pending_case_variadic = False
        self._cases_finalized = False
        self._else_action = None

    def _add_loop(self, iterable, stop):
        iter_arity = 0
        iter_variadic = False
        stop_pred = None
        stop_arity = 0
        stop_variadic = False

        if stop is not None:
            if not callable(stop):
                raise TypeError(
                    "Loop.iter(..., stop=...): stop must be callable, "
                    f"got {type(stop)}"
                )
            stop_pred = stop
            stop_arity, stop_variadic = self._analyze_callable(stop)

            if stop_arity == 0 and not stop_variadic:
                raise TypeError(
                    "Loop.iter(..., stop=...): stop predicate must take at least "
                    "one argument (extra and/or loop variable[s])."
                )

        self._loops.append(
            (iterable, iter_arity, iter_variadic, stop_pred, stop_arity, stop_variadic)
        )

    def _analyze_callable(self, fn):
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        positional = [
            p for p in params
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        has_var = any(
            p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
            for p in params
        )
        arity = len(positional)
        is_variadic = (arity == 0 and has_var)
        return arity, is_variadic

    def _analyze_predicate(self, predicate, where_label):
        arity, is_variadic = self._analyze_callable(predicate)

        if arity == 0 and not is_variadic:
            raise TypeError(
                f"{where_label}: predicate must take at least one argument "
                "(extra parameter[s] and/or loop variable[s])."
            )

        return arity, is_variadic

    def _iter_values(self, spec, spec_arity, spec_variadic, env_values, vars_so_far):
        if callable(spec):
            combined = list(env_values) + self._flatten_vars(vars_so_far)

            if spec_variadic:
                return spec(*combined)
            elif spec_arity > 0:
                return spec(*combined[:spec_arity])

        return spec

    def _flatten_vars(self, vars_so_far):
        flat = []
        for v in vars_so_far:
            if isinstance(v, tuple):
                flat.extend(v)
            else:
                flat.append(v)
        return flat


    def iter(self, iterable, stop=None, var=None):
        from typed.mods.general import var as _var

        if isinstance(var, str):
            _var(var)

        self._add_loop(iterable, stop=stop)
        return self

    def when(self, predicate):
        from typed.mods.helper.helper import _name
        if not callable(predicate):
            raise TypeError(
                "Loop.when(): expected a callable predicate.\n"
                f" ==> '{_name(predicate)}' has unexpected type '{type(predicate)}'"
            )

        arity, is_variadic = self._analyze_predicate(predicate, "Loop.when()")

        self._predicate = predicate
        self._pred_arity = arity
        self._pred_variadic = is_variadic
        return self

    def unless(self, predicate):
        from typed.mods.helper.helper import _name
        if not callable(predicate):
            raise TypeError(
                "Loop.unless(): expected a callable predicate.\n"
                f" ==> '{_name(predicate)}' has unexpected type '{type(predicate)}'"
            )

        arity, is_variadic = self._analyze_predicate(predicate, "Loop.unless()")

        def _negated(*args, **kwargs):
            if is_variadic:
                return not predicate(*args, **kwargs)
            else:
                return not predicate(*args[:arity], **kwargs)

        self._predicate = _negated
        self._pred_arity = arity
        self._pred_variadic = is_variadic
        return self

    def case(self, predicate):
        from typed.mods.helper.helper import _name
        if not callable(predicate):
            raise TypeError(
                "Loop.case(): expected a callable predicate.\n"
                f" ==> '{_name(predicate)}' has unexpected type '{type(predicate)}'"
            )

        if self._mode == "simple" and (self._cases or self._else_action):
            raise TypeError(
                "Loop.case(): internal state inconsistent; cases already defined "
                "while mode is 'simple'."
            )

        if self._pending_case_pred is not None:
            raise TypeError("Loop.case(): previous case has no associated .do().")

        self._mode = "cases"

        arity, is_variadic = self._analyze_predicate(predicate, "Loop.case()")

        self._pending_case_pred = predicate
        self._pending_case_arity = arity
        self._pending_case_variadic = is_variadic
        return self

    def end(self):
        if self._mode != "cases":
            raise TypeError("Loop.end(): .end() is only valid after .case().")

        if self._pending_case_pred is not None:
            raise TypeError("Loop.end(): last .case() has no associated .do().")

        if not self._cases:
            raise TypeError("Loop.end(): no cases defined before .end().")

        self._cases_finalized = True
        return self

    def do(self, action):
        num_loops = len(self._loops)
        extra_names = list(self._param_types.keys())
        num_extra = len(extra_names)

        env_only_pred_simple = (
            self._predicate is not None
            and not self._pred_variadic
            and self._pred_arity <= num_extra
        )


        if self._mode == "cases":
            env_only_pred = self._predicate is not None and (
                (not self._pred_variadic and self._pred_arity <= num_extra)
                or self._pred_variadic
            )
            if self._predicate is not None and not env_only_pred:
                raise TypeError(
                    "Loop.when()/unless(): when combined with .case()/.end(), "
                    "the predicate must depend only on extra parameters "
                    "(arity <= number of extra parameters)."
                )

            if callable(action):
                action_callable = action
            else:
                raise TypeError("Loop.do(): expected a callable or Expr as action.")

            if not self._cases_finalized:
                if self._pending_case_pred is None:
                    raise TypeError(
                        "Loop.do(): in case-mode, call .case(predicate) before .do(action)."
                    )
                self._cases.append(
                    (
                        self._pending_case_pred,
                        self._pending_case_arity,
                        self._pending_case_variadic,
                        action_callable,
                    )
                )
                self._pending_case_pred = None
                self._pending_case_arity = 0
                self._pending_case_variadic = False
                return self

            if self._else_action is not None:
                raise TypeError(
                    "Loop.do(): else-action already defined for this case-chain."
                )
            self._else_action = action_callable

            def _body(env_values):
                did_any = False
                last_result = None

                if env_only_pred:
                    if self._pred_variadic:
                        if not self._predicate(*env_values):
                            return did_any, last_result
                    else:
                        if not self._predicate(*env_values[: self._pred_arity]):
                            return did_any, last_result

                def _inner(level, vars_so_far):
                    nonlocal did_any, last_result

                    if level == num_loops:
                        flat = self._flatten_vars(vars_so_far)
                        combined = list(env_values) + flat

                        for pred, arity, is_var, act in self._cases:
                            if is_var:
                                cond = pred(*combined)
                            else:
                                cond = pred(*combined[:arity])
                            if cond:
                                last_result = act(*env_values, *flat)
                                did_any = True
                                return

                        if self._else_action is not None:
                            last_result = self._else_action(*env_values, *flat)
                            did_any = True
                        return

                    spec, spec_arity, spec_variadic, stop_pred, stop_arity, stop_variadic = self._loops[level]
                    for val in self._iter_values(spec, spec_arity, spec_variadic, env_values, vars_so_far):
                        if stop_pred is not None:
                            combined = (
                                list(env_values)
                                + self._flatten_vars(vars_so_far)
                                + [val]
                            )
                            if stop_variadic:
                                cond = stop_pred(*combined)
                            else:
                                cond = stop_pred(*combined[:stop_arity])
                            if cond:
                                break

                        _inner(level + 1, vars_so_far + [val])

                _inner(0, [])
                return did_any, last_result

            if num_extra == 0:
                def _runner():
                    did_any, last_result = _body(tuple())
                    return last_result
                _runner.__name__ = "loop_runner"
                return _runner

            params = [
                inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                for name in extra_names
            ]
            sig_for_impl = inspect.Signature(parameters=params)

            def _impl(*args, **kwargs):
                b = sig_for_impl.bind(*args, **kwargs)
                b.apply_defaults()
                env_values = tuple(b.arguments[name] for name in extra_names)

                did_any, last_result = _body(env_values)

                if not did_any:
                    return None

                if num_extra == 1 and last_result is None:
                    return env_values[0]

                return last_result

            from typed.mods.decorators import typed
            from typed.mods.types.base import Any

            _impl.__name__ = "loop_result"
            anns = {name: typ for name, typ in self._param_types.items()}
            anns["return"] = Any
            _impl.__annotations__ = anns
            _impl.__signature__ = sig_for_impl

            return typed(_impl)

        if not callable(action):
            raise TypeError("Loop.do(): expected a callable or Expr as action.")

        from typed.mods.types.func import Typed
        is_typed = isinstance(action, Typed)

        if is_typed:
            expected_arity = len(action.domain)
            is_variadic_action = False
        else:
            expected_arity, is_variadic_action = self._analyze_callable(action)

        if (not is_variadic_action) and expected_arity < num_extra:
            kind = "typed action" if is_typed else "action"
            raise TypeError(
                f"Loop.do(): {kind} has too few parameters for the extra arguments.\n"
                f" ==> expected at least {num_extra} (extra={num_extra}), "
                f"got {expected_arity}."
            )

        def _body(env_values):
            did_any = False
            last_result = None

            if env_only_pred_simple:
                if not self._predicate(*env_values[: self._pred_arity]):
                    return did_any, last_result

            def _inner(level, vars_so_far):
                nonlocal did_any, last_result

                if level == num_loops:
                    flat = self._flatten_vars(vars_so_far)

                    if self._predicate is not None and not env_only_pred_simple:
                        combined = list(env_values) + flat
                        if self._pred_variadic:
                            if not self._predicate(*combined):
                                return
                        else:
                            if not self._predicate(*combined[: self._pred_arity]):
                                return

                    last_result = action(*env_values, *flat)
                    did_any = True
                    return

                spec, spec_arity, spec_variadic, stop_pred, stop_arity, stop_variadic = self._loops[level]
                for val in self._iter_values(spec, spec_arity, spec_variadic, env_values, vars_so_far):
                    if stop_pred is not None:
                        combined = (
                            list(env_values)
                            + self._flatten_vars(vars_so_far)
                            + [val]
                        )
                        if stop_variadic:
                            cond = stop_pred(*combined)
                        else:
                            cond = stop_pred(*combined[:stop_arity])
                        if cond:
                            break

                    _inner(level + 1, vars_so_far + [val])


            _inner(0, [])
            return did_any, last_result

        if num_extra == 0:
            def _runner():
                did_any, last_result = _body(tuple())
                return last_result
            _runner.__name__ = "loop_runner"
            return _runner

        params = [
            inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            for name in extra_names
        ]
        sig_for_impl = inspect.Signature(parameters=params)

        def _impl(*args, **kwargs):
            b = sig_for_impl.bind(*args, **kwargs)
            b.apply_defaults()
            env_values = tuple(b.arguments[name] for name in extra_names)

            did_any, last_result = _body(env_values)

            if not did_any:
                return None

            if num_extra == 1 and last_result is None:
                return env_values[0]

            return last_result

        from typed.mods.decorators import typed
        from typed.mods.types.base import Any
        _impl.__name__ = "loop_result"
        anns = {name: typ for name, typ in self._param_types.items()}
        anns["return"] = Any
        _impl.__annotations__ = anns
        _impl.__signature__ = sig_for_impl

        return typed(_impl)
