def _null_model(typ):
    required = dict(getattr(typ, '_required_attributes_and_types', {}))
    optional = getattr(typ, '_optional_attributes_and_defaults', {})
    ordered_keys = getattr(typ, '_ordered_keys', None)
    all_keys = []
    data = {}
    if ordered_keys:
        for name in ordered_keys:
            if name in required:
                val = _null(required[name])
                data[name] = val
            elif name in optional:
                wrapper = optional[name]
                if wrapper.default_value is not None:
                    data[name] = wrapper.default_value
                else:
                    data[name] = _null(wrapper.type)
            else:
                pass
    else:
        for name, field_type in required.items():
            data[name] = _null(field_type)
        for name, wrapper in optional.items():
            if wrapper.default_value is not None:
                data[name] = wrapper.default_value
            else:
                data[name] = _null(wrapper.type)
    try:
        return typ(**data)
    except Exception as e:
        return None

def _null(typ):
    if hasattr(typ, '__null__') and typ.__null__ is not None:
        return typ.__null__

    try:
        from typed.mods.models import MODEL
    except Exception:
        return None

    if isinstance(typ, MODEL):
        val = _null_model(typ)
        try:
            typ.__null__ = val
        except Exception:
            pass
        return val

    return None

def _null_from_list(*types):
    null = None
    for t in types:
        if _null(t) is not None:
            null = _null(t)
            break
    return null
