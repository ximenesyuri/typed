from f_core.mods.type.helper_ import flat_
from f_core.mods.op.other_ import (
    tuple_type_,
    list_type_,
    set_type_,
    dict_type_
)

def ntuple_type_(*types, size=None):
    if not isinstance(size, int) or size < 0:
        raise ValueError("size must be a non-negative integer.")

    flat_types, _ = flat_(*types)
    base_tuple_type = tuple_type_(*flat_types)

    class _ntuple(base_tuple_type.__class__):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, tuple):
                return False
            if len(instance) != size:
                return False
            return all(any(isinstance(item, t) for t in flat_types) for item in instance)

        def check(self, instance):
            if not isinstance(instance, tuple):
                return False
            if len(instance) != size:
                return False
            return all(any(isinstance(item, t) for t in self.__types__) for item in instance)

    class_name = f"ntuple({', '.join(t.__name__ for t in flat_types)}, size={size})"
    return _ntuple(class_name, (base_tuple_type,), {'__types__': flat_types})

def nlist_type_(*types, size=None):
    if not isinstance(size, int) or size < 0:
        raise ValueError("size must be a non-negative integer.")

    flat_types, _ = flat_(*types)
    base_list_type = list_type_(*flat_types)

    class _nlist(base_list_type.__class__):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, list):
                return False
            if len(instance) != size:
                return False
            return all(any(isinstance(item, t) for t in flat_types) for item in instance)

        def check(self, instance):
            if not isinstance(instance, list):
                return False
            if len(instance) != size:
                return False
            return all(any(isinstance(item, t) for t in self.__types__) for item in instance)

    class_name = f"nlist({', '.join(t.__name__ for t in flat_types)}, size={size})"
    return _nlist(class_name, (base_list_type,), {'__types__': flat_types})


def nset_type_(*types, size=None):
    if not isinstance(size, int) or size < 0:
        raise ValueError("size must be a non-negative integer.")

    flat_types, _ = flat_(*types)
    base_set_type = set_type_(*flat_types)

    class _nset(base_set_type.__class__):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, set):
                return False
            if len(instance) != size:
                return False
            return all(any(isinstance(item, t) for t in flat_types) for item in instance)

        def check(self, instance):
            if not isinstance(instance, set):
                return False
            if len(instance) != size:
                return False
            return all(any(isinstance(item, t) for t in self.__types__) for item in instance)

    class_name = f"nset({', '.join(t.__name__ for t in flat_types)}, size={size})"
    return _nset(class_name, (base_set_type,), {'__types__': flat_types})

def ndict_type_(key_types, value_types, size=None):
    if not isinstance(size, int) or size < 0:
        raise ValueError("size must be a non-negative integer.")

    key_flat_types, _ = flat_(*key_types)
    value_flat_types, _ = flat_(*value_types)
    base_dict_type = dict_type_(key_flat_types, value_flat_types)
    
    class _ndict(base_dict_type.__class__):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, dict):
                return False
            if len(instance) != size:
                return False
            return (
                all(any(isinstance(k, t) for t in key_flat_types) for k in instance) and
                all(any(isinstance(v, t) for t in value_flat_types) for v in instance.values())
            )

        def check(self, instance):
            if not isinstance(instance, dict):
                return False
            if len(instance) != size:
                return False
            return (
                all(any(isinstance(k, t) for t in self.__types__[0]) for k in instance) and
                all(any(isinstance(v, t) for t in self.__types__[1]) for v in instance.values())
            )

    class_name = f"ndict({{{', '.join(t.__name__ for t in key_flat_types)}}}:{{{', '.join(t.__name__ for t in value_flat_types)}}}, size={size})"
    return _ndict(class_name, (base_dict_type,), {'__types__': (key_flat_types, value_flat_types)})
