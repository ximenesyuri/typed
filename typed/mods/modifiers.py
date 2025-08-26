def symmetrization(func=None, *, key=None):
    """
    Decorator that makes a function symmetric in its positional arguments:
      – All permutations of *args get sorted (by key or by value, or by repr())
        before you actually invoke the underlying function.
      – **kwargs are left untouched.
    """
    def _decorate(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if key is not None:
                try:
                    ordered = tuple(sorted(args, key=key))
                except Exception as e:
                    raise ValueError(f"symmetric: can't sort args with key={key!r}: {e}")
            else:
                try:
                    ordered = tuple(sorted(args))
                except TypeError:
                    ordered = tuple(sorted(args, key=lambda x: repr(x)))
            return f(*ordered, **kwargs)
        return wrapper
    if func is None:
        return _decorate
    else:
        return _decorate(func)
