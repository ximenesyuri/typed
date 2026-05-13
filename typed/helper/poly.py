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


class _Checker:
    def __init__(self, values, aggregator):
        self.values = values
        self.aggregator = aggregator

    def _evaluate_comparison(self, op, other):
        results = []
        errors = []

        for value in self.values:
            try:
                result = op(value, other)
                results.append(result)
            except Exception as e:
                errors.append(e)
        if len(errors) == len(self.values) and len(self.values) > 0:
            raise errors[0]
        return self.aggregator(results) if results else False

    def __eq__(self, other):
        return self._evaluate_comparison(lambda x, y: x == y, other)

    def __ne__(self, other):
        return self._evaluate_comparison(lambda x, y: x != y, other)

    def __lt__(self, other):
        return self._evaluate_comparison(lambda x, y: x < y, other)

    def __le__(self, other):
        return self._evaluate_comparison(lambda x, y: x <= y, other)

    def __gt__(self, other):
        return self._evaluate_comparison(lambda x, y: x > y, other)

    def __ge__(self, other):
        return self._evaluate_comparison(lambda x, y: x >= y, other)

    def __contains__(self, item):
        results = []
        errors = []

        for value in self.values:
            try:
                result = item in value
                results.append(result)
            except Exception as e:
                errors.append(e)

        if len(errors) == len(self.values) and len(self.values) > 0:
            raise errors[0]

        return self.aggregator(results) if results else False

    def is_(self, other):
        results = [x is other for x in self.values]
        return self.aggregator(results)

    def is_not(self, other):
        results = [x is not other for x in self.values]
        return self.aggregator(results)

class Checker:
    def __init__(self, aggregator):
        self.aggregator = aggregator

    def __call__(self, *args):
        return _Checker(args, self.aggregator)
