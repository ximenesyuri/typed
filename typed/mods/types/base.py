from typed.mods.meta.base import (
    _TYPE_, _ABSTRACT_, _UNIVERSAL_,
    _META_, _DISCOURSE_, _PARAMETRIC_,
    NILL, ANY,
    STR, INT, FLOAT, BOOL, BYTES,
    TUPLE, LIST, SET, DICT,
    PATTERN
)

Nill = NILL("Nill", (), {
    "__display__": "Nill",
    "__null__": None
})

class TYPE(metaclass=_TYPE_):
    __display__ = "TYPE"
    __null__ = Nill
    __builtin__ = type

    @staticmethod
    def __convert__(obj, t, _cls_cache=None, _meta_cache=None):
        from typed.mods.helper.helper import _name
        from inspect import isclass

        def _convert_property(prop, t, _cls_cache, _meta_cache):
            def getter(self):
                value = prop.fget(self)
                try:
                    return TYPE.__convert__(value, t, _cls_cache, _meta_cache)
                except Exception:
                    return value
            setter = None
            deleter = None
            if prop.fset:
                def setter(self, val):
                    prop.fset(self, val)
            if prop.fdel:
                def deleter(self):
                    prop.fdel(self)
            return property(getter, setter, deleter, prop.__doc__)

        if t is not TYPE:
            raise TypeError(
                "Wrong type in TYPE.__convert__:\n"
                f" ==> '{_name(t)}': has an unexpected type\n"
                "     [expected_type] subtype of 'TYPE'\n"
                f"     [received_type] '{_name(TYPE(t))}'"
            )

        if _cls_cache is None:
            _cls_cache = {}
        if _meta_cache is None:
            _meta_cache = {}

        if isinstance(obj, TYPE):
            return obj
        if obj in _cls_cache:
            return _cls_cache[obj]

        if not isclass(obj):
            raise TypeError("obj must be a class.")

        orig_meta = type(obj)
        if orig_meta in _meta_cache:
            meta_in_type = _meta_cache[orig_meta]
        else:
            if orig_meta is type:
                base_metas = (_TYPE_,)
            else:
                base_metas = tuple(
                    TYPE.__convert__(b, t, _cls_cache, _meta_cache)
                    for b in orig_meta.__bases__
                ) or (_TYPE_,)
            meta_name = f"CONVERTED({_name(obj)})"

            meta_attrs = {}
            for name in dir(orig_meta):
                if name.startswith('__') and name.endswith('__'):
                    if name in ('__module__', '__qualname__'):
                        val = getattr(orig_meta, name)
                        if isinstance(val, str):
                            meta_attrs[name] = val
                    continue
                try:
                    meta_attrs[name] = getattr(orig_meta, name)
                except Exception:
                    pass

            if '__instancecheck__' not in meta_attrs:
                meta_attrs['__instancecheck__'] = lambda cls, instance: type.__instancecheck__(obj, instance)

            meta_in_type = type(meta_name, base_metas, meta_attrs)
            _meta_cache[orig_meta] = meta_in_type

        converted_bases = tuple(
            TYPE.__convert__(base, t, _cls_cache, _meta_cache)
            for base in obj.__bases__
        )

        class_name = _name(obj).capitalize()
        orig_attrs = {}

        slots = getattr(obj, '__slots__', ())
        if isinstance(slots, str):
            slots = (slots,)

        for name in dir(obj):
            if name in slots:
                continue
            if name.startswith('__') and name.endswith('__'):
                if name in ('__module__', '__qualname__'):
                    val = getattr(obj, name)
                    if isinstance(val, str):
                        orig_attrs[name] = val
                elif name == '__doc__':
                    val = getattr(obj, name, None)
                    if val:
                        orig_attrs[name] = val
                continue
            try:
                attr = getattr(obj, name)
                if isinstance(attr, property):
                    orig_attrs[name] = _convert_property(attr, t, _cls_cache, _meta_cache)
                else:
                    orig_attrs[name] = attr
            except Exception:
                pass

        orig_attrs.update({"__display__": class_name})

        if slots:
            orig_attrs['__slots__'] = slots

        for slot in slots:
            if slot in orig_attrs:
                del orig_attrs[slot]

        new_cls = meta_in_type(class_name, converted_bases, orig_attrs)
        _cls_cache[obj] = new_cls
        return new_cls

ABSTRACT = _ABSTRACT_("ABSTRACT", (TYPE,), {
    "__display__": "ABSTRACT",
    "__null__": NILL
})

UNIVERSAL = _UNIVERSAL_("UNIVERSAL", (TYPE,), {
    "__display__": "UNIVERSAL",
    "__null__": NILL
})

META = _META_("META", (TYPE,), {
    "__display__": "META",
    "__null__": NILL
})

DISCOURSE = _DISCOURSE_("DISCOURSE", (TYPE,), {
    "__display__": "DISCOURSE",
    "__null__": NILL
})

PARAMETRIC = _PARAMETRIC_("PARAMETRIC", (TYPE,), {
    "__display__": "PARAMETRIC",
    "__null__": NILL
})

Int = INT("Int", (), {
    "__display__": "Int",
    "__null__": 0,
    "__builtin__": int
})
Float = FLOAT("Int", (), {
    "__display__": "Float",
    "__null__": 0.0,
    "__builtin__": float
})
Bool = BOOL("Bool", (), {
    "__display__": "Bool",
    "__null__": False,
    "__builtin__": bool
})

class Str(metaclass=STR):
    def __len__(self, obj):
        return len(obj)
    __display__ = "Str"
    __null__ = "",
    __builtin__ = str

Any = ANY("Any", (), {
    "__display__": "Any",
    "__null__": None
})
Self = Any
Cls  = Any
Bytes = BYTES("Bytes", (), {
    "__display__": "Bytes",
    "__null__": bytes(),
    "__builtin__": bytes
})
Tuple = TUPLE("Tuple", (), {
    "__display__": "Tuple",
    "__null__": tuple(),
    "__builtin__": tuple
})
List = LIST("List", (), {
    "__display__": "List",
    "__null__": list(),
    "__builtin__": list
})
Set = SET("Set", (), {
    "__display__": "Set",
    "__null__": set(),
    "__builtin__": set
})

class Dict(metaclass=DICT):
    __display__ = "Dict"
    __null__    = dict()
    __builtin__ = dict

    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    def __contains__(self, key):
        return key in self.__dict__

Pattern = PATTERN("Pattern", (Str,), {"__display__": "Pattern", "__null__": ""})
