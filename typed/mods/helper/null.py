def _null_model(typ):
    """
    Build the null (empty) instance of a Model‐type:
      – for each required field, take _null(field_type)
      – for each optional field, take wrapper.default_value
        (or fall back to _null(wrapper.type))
    """
    required = dict(getattr(typ, '_required_attributes_and_types', {}))
    optional = getattr(typ, '_optional_attributes_and_defaults', {})
    data = {}
    for name, field_type in required.items():
        data[name] = _null(field_type)
    for name, wrapper in optional.items():
        if wrapper.default_value is not None:
            data[name] = wrapper.default_value
        else:
            data[name] = _null(wrapper.type)
    return typ(**data)

def _null(typ):
    if hasattr(typ, '__null__'):
        return typ.__null__
    return None

def _null_from_list(*types):
    null = None
    for t in types:
        if _null(t) is not None:
            null = _null(t)
            break
    return null
