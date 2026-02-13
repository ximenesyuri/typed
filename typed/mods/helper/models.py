import json
from threading import local
from contextlib import contextmanager
from typed.mods.meta.models import _MODEL_FACTORY_
from typed.mods.types.base import TYPE
from typed.mods.helper.helper import _name

_dynamic_default_state = local()

def _get_dynamic_default_env():
    env = getattr(_dynamic_default_state, "env", None)
    if env is None:
        env = {}
        _dynamic_default_state.env = env
    return env

def _get_dynamic_default_stack():
    stack = getattr(_dynamic_default_state, "stack", None)
    if stack is None:
        stack = []
        _dynamic_default_state.stack = stack
    return stack

def _get_current_model_and_entity():
    stack = getattr(_dynamic_default_state, "stack", None)
    if not stack:
        return None, None
    model_cls = stack[-1]
    env = _get_dynamic_default_env()
    return model_cls, env.get(model_cls)

@contextmanager
def _dynamic_default_context(model_cls, entity_dict):
    env = _get_dynamic_default_env()
    stack = _get_dynamic_default_stack()
    prev = env.get(model_cls, None)
    stack.append(model_cls)
    env[model_cls] = entity_dict
    try:
        yield
    finally:
        stack.pop()
        if prev is None:
            env.pop(model_cls, None)
        else:
            env[model_cls] = prev

def _resolve_operand(obj):
    if isinstance(obj, FieldRef):
        return obj.resolve()
    if isinstance(obj, Expr):
        return obj()
    if callable(obj):
        return obj()
    return obj

class Expr:
    def __init__(self, func): self._func = func
    def __call__(self): return self._func()
    def __getattr__(self, name):
        def fn():
            resolved = self()
            if hasattr(resolved, name):
                attr = getattr(resolved, name)
                if callable(attr):
                    def method_wrapper(*args, **kwargs):
                        current_resolved = self()
                        method = getattr(current_resolved, name)
                        return method(*args, **kwargs)
                    return method_wrapper
                return attr
            else:
                raise AttributeError(f"'{type(resolved).__name__}' object has no attribute '{name}'")
        return fn

    def __str__(self): return str(self())
    def __int__(self): return int(self())
    def __float__(self): return float(self())
    def __bool__(self): return bool(self())
    def __len__(self):  return len(self())
    def __iter__(self): return iter(self())
    def __getitem__(self, key): return self()[key]
    def __contains__(self, item): return item in self()
    def __eq__(self, other): return self() == other
    def __ne__(self, other): return self() != other
    def __hash__(self): return hash(self())
    def __repr__(self): return repr(self())

    def __add__(self, other):
        def fn():
            left = self()
            right = _resolve_operand(other)
            return left + right
        return Expr(fn)

    def __radd__(self, other):
        def fn():
            left = _resolve_operand(other)
            right = self()
            return left + right
        return Expr(fn)

    def __sub__(self, other):
        def fn():
            left = self()
            right = _resolve_operand(other)
            return left - right
        return Expr(fn)

    def __rsub__(self, other):
        def fn():
            left = _resolve_operand(other)
            right = self()
            return left - right
        return Expr(fn)

    def __mul__(self, other):
        def fn():
            left = self()
            right = _resolve_operand(other)
            return left * right
        return Expr(fn)

    def __rmul__(self, other):
        def fn():
            left = _resolve_operand(other)
            right = self()
            return left * right
        return Expr(fn)

    def __truediv__(self, other):
        def fn():
            left = self()
            right = _resolve_operand(other)
            return left / right
        return Expr(fn)

    def __rtruediv__(self, other):
        def fn():
            left = _resolve_operand(other)
            right = self()
            return left / right
        return Expr(fn)

    def __floordiv__(self, other):
        def fn():
            left = self()
            right = _resolve_operand(other)
            return left // right
        return Expr(fn)

    def __rfloordiv__(self, other):
        def fn():
            left = _resolve_operand(other)
            right = self()
            return left // right
        return Expr(fn)

    def __mod__(self, other):
        def fn():
            left = self()
            right = _resolve_operand(other)
            return left % right
        return Expr(fn)

    def __rmod__(self, other):
        def fn():
            left = _resolve_operand(other)
            right = self()
            return left % right
        return Expr(fn)

    def __pow__(self, other):
        def fn():
            left = self()
            right = _resolve_operand(other)
            return left ** right
        return Expr(fn)

    def __rpow__(self, other):
        def fn():
            left = _resolve_operand(other)
            right = self()
            return left ** right
        return Expr(fn)

class _FieldProxy:
    def __init__(self, value, field_type):
        self._value = value
        self._field_type = field_type

    def __getattr__(self, name):
        if hasattr(self._value, name):
            return getattr(self._value, name)
        elif hasattr(self._field_type, name):
            attr = getattr(self._field_type, name)
            if callable(attr):
                return attr
            return attr
        elif hasattr(self._field_type, '__builtin__'):
            builtin_type = getattr(self._field_type, '__builtin__')
            if hasattr(builtin_type, name):
                attr = getattr(builtin_type, name)
                if callable(attr):
                    return attr
                return attr
        else:
            raise AttributeError(f"'{name}' not found in value, field type, or its __builtin__")

    def __repr__(self):
        return f"_FieldProxy({repr(self._value)}, {repr(self._field_type)})"

    def __str__(self): return str(self._value)
    def __int__(self): return int(self._value)
    def __float__(self): return float(self._value)
    def __bool__(self): return bool(self._value)
    def __len__(self): return len(self._value)
    def __iter__(self): return iter(self._value)
    def __getitem__(self, key): return self._value[key]
    def __ne__(self, other): return not self.__eq__(other)
    def __hash__(self): return hash(self._value)
    def __contains__(self, item): return item in self._value

    def __eq__(self, other):
        if isinstance(other, _FieldProxy):
            return self._value == other._value
        return self._value == other
    def __add__(self, other):
        if isinstance(other, _FieldProxy):
            return self._value + other._value
        return self._value + other

    def __radd__(self, other):
        if isinstance(other, _FieldProxy):
            return other._value + self._value
        return other + self._value

    def __sub__(self, other):
        if isinstance(other, _FieldProxy):
            return self._value - other._value
        return self._value - other

    def __rsub__(self, other):
        if isinstance(other, _FieldProxy):
            return other._value - self._value
        return other - self._value

    def __mul__(self, other):
        if isinstance(other, _FieldProxy):
            return self._value * other._value
        return self._value * other

    def __rmul__(self, other):
        if isinstance(other, _FieldProxy):
            return other._value * self._value
        return other * self._value

    def __truediv__(self, other):
        if isinstance(other, _FieldProxy):
            return self._value / other._value
        return self._value / other

    def __rtruediv__(self, other):
        if isinstance(other, _FieldProxy):
            return other._value / self._value
        return other / self._value

    def __floordiv__(self, other):
        if isinstance(other, _FieldProxy):
            return self._value // other._value
        return self._value // other

    def __rfloordiv__(self, other):
        if isinstance(other, _FieldProxy):
            return other._value // self._value
        return other // self._value

    def __mod__(self, other):
        if isinstance(other, _FieldProxy):
            return self._value % other._value
        return self._value % other

    def __rmod__(self, other):
        if isinstance(other, _FieldProxy):
            return other._value % self._value
        return other % self._value

    def __pow__(self, other):
        if isinstance(other, _FieldProxy):
            return self._value ** other._value
        return self._value ** other

    def __rpow__(self, other):
        if isinstance(other, _FieldProxy):
            return other._value ** self._value
        return other ** self._value


class FieldRef:
    def __init__(self, attr_path):
        if isinstance(attr_path, str):
            attr_path = attr_path.lstrip(".")
            self.attr_path = attr_path.split(".") if attr_path else []
        else:
            self.attr_path = list(attr_path)

    def _resolve_instance_dict(self):
        model_cls, entity = _get_current_model_and_entity()
        if entity is None:
            raise RuntimeError(
                f"No dynamic default context active while resolving FieldRef "
                f"{self.attr_path} (no current model)."
            )
        return entity

    def _get_field_type(self):
        model_cls, _ = _get_current_model_and_entity()
        if model_cls is None:
            return None

        attrs_meta = getattr(model_cls, 'attrs', None)
        if attrs_meta is None:
            return None

        top = self.attr_path[0] if self.attr_path else None
        if top is None or top not in attrs_meta:
            return None

        return attrs_meta[top]['type']

    def resolve(self):
        current = self._resolve_instance_dict()
        model_cls, _ = _get_current_model_and_entity()
        attrs_meta = getattr(model_cls, 'attrs', None)
        if attrs_meta is not None:
            top = self.attr_path[0] if self.attr_path else None
            if top not in attrs_meta:
                raise AttributeError(
                    f"Dynamic default refers to unknown field '{top}' in model "
                    f"{getattr(model_cls, '__name__', model_cls)}"
                )

        for part in self.attr_path:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = getattr(current, part)

        if len(self.attr_path) == 1 and attrs_meta is not None and current is not None:
            top = self.attr_path[0]
            if top in attrs_meta:
                field_type = attrs_meta[top]['type']
                if field_type is not None:
                    return _FieldProxy(current, field_type)
        return current

    def __getattr__(self, name):
        def expr_func(*args, **kwargs):
            try:
                resolved = self.resolve()
                if hasattr(resolved, name):
                    attr = getattr(resolved, name)
                    if callable(attr):
                        return attr(*args, **kwargs)
                    return attr
                raise AttributeError(f"'{type(resolved).__name__}' object has no attribute '{name}'")
            except RuntimeError:
                    if not args and not kwargs:
                        def deferred_call(*call_args, **call_kwargs):
                            final_resolved = self.resolve()
                            if hasattr(final_resolved, name):
                                final_attr = getattr(final_resolved, name)
                                if callable(final_attr):
                                    return final_attr(*call_args, **call_kwargs)
                                return final_attr
                            raise AttributeError(f"'{type(final_resolved).__name__}' object has no attribute '{name}'")
                        return deferred_call
                    else:
                        raise
        return Expr(expr_func)

    def __str__(self):
        try:
            resolved = self.resolve()
            return str(resolved)
        except RuntimeError:
            return f"<FieldRef {self.attr_path}>"

    def __int__(self):
        try:
            resolved = self.resolve()
            return int(resolved)
        except RuntimeError:
            raise TypeError(f"Cannot convert FieldRef {self.attr_path} to int without context")

    def __float__(self):
        try:
            resolved = self.resolve()
            return float(resolved)
        except RuntimeError:
            raise TypeError(f"Cannot convert FieldRef {self.attr_path} to float without context")

    def __bool__(self):
        try:
            resolved = self.resolve()
            return bool(resolved)
        except RuntimeError:
            raise TypeError(f"Cannot convert FieldRef {self.attr_path} to bool without context")

    def __len__(self):
        try:
            resolved = self.resolve()
            return len(resolved)
        except RuntimeError:
            raise TypeError(f"Cannot get length of FieldRef {self.attr_path} without context")

    def __iter__(self):
        try:
            resolved = self.resolve()
            return iter(resolved)
        except RuntimeError:
            raise TypeError(f"Cannot iterate over FieldRef {self.attr_path} without context")

    def __getitem__(self, key):
        try:
            resolved = self.resolve()
            return resolved[key]
        except RuntimeError:
            raise TypeError(f"Cannot index FieldRef {self.attr_path} without context")

    def __contains__(self, item):
        try:
            resolved = self.resolve()
            return item in resolved
        except RuntimeError:
            raise TypeError(f"Cannot check membership in FieldRef {self.attr_path} without context")

    def __eq__(self, other):
        try:
            resolved = self.resolve()
            return resolved == other
        except RuntimeError:
            return False

    def __ne__(self, other):
        try:
            resolved = self.resolve()
            return resolved != other
        except RuntimeError:
            return True

    def __hash__(self):
        try:
            resolved = self.resolve()
            return hash(resolved)
        except RuntimeError:
            raise TypeError(f"Cannot hash FieldRef {self.attr_path} without context")

    def __repr__(self):
        try:
            resolved = self.resolve()
            return repr(resolved)
        except RuntimeError:
            return f"<FieldRef {self.attr_path}>"

    def __add__(self, other):
        try:
            resolved = self.resolve()
            return resolved + other
        except RuntimeError:
            raise TypeError(f"Cannot add FieldRef {self.attr_path} without context")

    def __radd__(self, other):
        try:
            resolved = self.resolve()
            return other + resolved
        except RuntimeError:
            raise TypeError(f"Cannot add to FieldRef {self.attr_path} without context")

    def __sub__(self, other):
        try:
            resolved = self.resolve()
            return resolved - other
        except RuntimeError:
            raise TypeError(f"Cannot subtract FieldRef {self.attr_path} without context")

    def __rsub__(self, other):
        try:
            resolved = self.resolve()
            return other - resolved
        except RuntimeError:
            raise TypeError(f"Cannot subtract from FieldRef {self.attr_path} without context")

    def __mul__(self, other):
        try:
            resolved = self.resolve()
            return resolved * other
        except RuntimeError:
            raise TypeError(f"Cannot multiply FieldRef {self.attr_path} without context")

    def __rmul__(self, other):
        try:
            resolved = self.resolve()
            return other * resolved
        except RuntimeError:
            raise TypeError(f"Cannot multiply with FieldRef {self.attr_path} without context")

    def __truediv__(self, other):
        try:
            resolved = self.resolve()
            return resolved / other
        except RuntimeError:
            raise TypeError(f"Cannot divide FieldRef {self.attr_path} without context")

    def __rtruediv__(self, other):
        try:
            resolved = self.resolve()
            return other / resolved
        except RuntimeError:
            raise TypeError(f"Cannot divide by FieldRef {self.attr_path} without context")

    def __floordiv__(self, other):
        try:
            resolved = self.resolve()
            return resolved // other
        except RuntimeError:
            raise TypeError(f"Cannot floor divide FieldRef {self.attr_path} without context")

    def __rfloordiv__(self, other):
        try:
            resolved = self.resolve()
            return other // resolved
        except RuntimeError:
            raise TypeError(f"Cannot floor divide by FieldRef {self.attr_path} without context")

    def __mod__(self, other):
        try:
            resolved = self.resolve()
            return resolved % other
        except RuntimeError:
            raise TypeError(f"Cannot modulo FieldRef {self.attr_path} without context")

    def __rmod__(self, other):
        try:
            resolved = self.resolve()
            return other % resolved
        except RuntimeError:
            raise TypeError(f"Cannot modulo by FieldRef {self.attr_path} without context")

    def __pow__(self, other):
        try:
            resolved = self.resolve()
            return resolved ** other
        except RuntimeError:
            raise TypeError(f"Cannot power FieldRef {self.attr_path} without context")

    def __rpow__(self, other):
        try:
            resolved = self.resolve()
            return other ** resolved
        except RuntimeError:
            raise TypeError(f"Cannot power by FieldRef {self.attr_path} without context")

def _expr_function(fn):
    def wrapper(*args, **kwargs):
        for a in args:
            if not isinstance(a, (Expr, FieldRef)):
                raise TypeError(
                    f"{fn.__name__} expects Expr/FieldRef arguments inside Default; "
                    f"got {type(a)}"
                )
        for k, v in kwargs.items():
            if not isinstance(v, (Expr, FieldRef)):
                raise TypeError(
                    f"{fn.__name__} expects Expr/FieldRef kwargs inside Default; "
                    f"'{k}' has type {type(v)}"
                )
        def eval_():
            resolved_args = [_resolve_operand(a) for a in args]
            resolved_kwargs = {k: _resolve_operand(v) for k, v in kwargs.items()}
            return fn(*resolved_args, **resolved_kwargs)
        return Expr(eval_)
    return wrapper

class _Optional:
    def __init__(self, typ, default_value):
        self.type = typ
        self.default_value = default_value
        self.__display__ = f"Optional({_name(typ)}, {default_value})"

MODEL_FACTORY = _MODEL_FACTORY_('MODEL_FACTORY', (TYPE,), {})

def _ensure_iterable_conditions(conditions):
    if callable(conditions):
        return [conditions]
    if isinstance(conditions, (list, tuple)):
        if all(callable(f) for f in conditions):
            return list(conditions)
    raise TypeError("__conditions__ must be a callable or a list/tuple of callables")

def _ordered_keys(attributes_and_types, optional_defaults):
    return [k for k, _ in attributes_and_types]

def _materialize_if_lazy(model):
    if getattr(model, "is_lazy", False):
        materialize = getattr(model, "_materialize", None)
        if callable(materialize):
            try:
                return materialize()
            except Exception:
                return model
    return model

def _process_extends(__extends__):
    extended_models = []
    if __extends__ is not None:
        if isinstance(__extends__, list):
            extended_models.extend(__extends__)
        else:
            extended_models.append(__extends__)

    extended_models = [_materialize_if_lazy(m) for m in extended_models]
    return extended_models

def _merge_attrs(extended_models, new_kwargs):
    combined = {}

    for parent in extended_models:
        parent_required = dict(getattr(parent, '_required_attributes_and_types', ()))
        parent_optional = getattr(parent, '_optional_attributes_and_defaults', {})

        for k, opt in parent_optional.items():
            if k not in combined:
                combined[k] = opt

        for k, typ in parent_required.items():
            if k not in parent_optional and k not in combined:
                combined[k] = typ

    combined.update(new_kwargs)
    return combined

def _attrs(kwargs):
    processed_attributes_and_types = []
    required_attribute_keys = set()
    optional_attributes_and_defaults = {}
    for key, value in kwargs.items():
        if isinstance(value, _Optional):
            processed_attributes_and_types.append((key, value.type))
            optional_attributes_and_defaults[key] = value
        elif isinstance(value, TYPE) or hasattr(value, '__instancecheck__'):
            processed_attributes_and_types.append((key, value))
            required_attribute_keys.add(key)
        else:
            raise TypeError(
                f"All argument values must be types or OptionalArg instances. Invalid type for '{key}': {type(value)}"
            )
    return tuple(processed_attributes_and_types), required_attribute_keys, optional_attributes_and_defaults

def _optional(type_hint, default, is_nullable):
    from typed.mods.models import Optional

    if isinstance(type_hint, _Optional):
        return type_hint

    if is_nullable:
        if default is not None:
            return Optional(type_hint, default)
        try:
            from typed import null
            return Optional(type_hint, null(type_hint))
        except Exception:
            try:
                return Optional(type_hint, type_hint())
            except Exception:
                return Optional(type_hint, None)
    else:
        return Optional(type_hint, default)

def _attach_model_attrs(child_model, parent_models):
    if not hasattr(child_model, 'extends'):
        child_model.extends = tuple(parent_models)
        child_model.extended_by = ()
        child_model.is_model = True
        child_model.is_exact = False
        child_model.is_ordered = False
        child_model.is_rigid = False
        child_model.is_optional = False
        child_model.is_mandatory = False

        for parent in parent_models:
            try:
                prev = getattr(parent, 'extended_by', ())
                if not isinstance(prev, tuple):
                    prev = tuple(prev)
                parent.extended_by = prev + (child_model,)
            except Exception:
                pass

    reqs = getattr(child_model, '_defined_required_attributes', {})
    opts = getattr(child_model, '_defined_optional_attributes', {})

    all_meta = {}
    for name, typ in reqs.items():
        all_meta[name] = {
            'type':     typ,
            'optional': False,
            'default':  None
        }
    for name, wrapper in opts.items():
        all_meta[name] = {
            'type':     wrapper.type,
            'optional': True,
            'default':  wrapper.default_value
        }

    child_model.attrs = all_meta

    child_model.optional_attrs = {
        name: meta
        for name, meta in all_meta.items()
        if meta['optional']
    }

    child_model.mandatory_attrs = {
        name: meta
        for name, meta in all_meta.items()
        if not meta['optional']
    }

def _update_model_attr(cls, name, value):
    current_kwargs = {}
    ordered_keys_list = list(getattr(cls, '_ordered_keys', []))
    req_attrs = getattr(cls, '_defined_required_attributes', {})
    opt_attrs = getattr(cls, '_defined_optional_attributes', {})

    current_keys = set(ordered_keys_list)

    if name not in current_keys:
        ordered_keys_list.append(name)
    for k in ordered_keys_list:
        if k == name:
            current_kwargs[k] = value
        elif k in req_attrs:
            current_kwargs[k] = req_attrs[k]
        elif k in opt_attrs:
            current_kwargs[k] = opt_attrs[k]

    new_attrs_tuple, new_req_keys, new_opt_attrs = _attrs(current_kwargs)
    new_ordered_keys = _ordered_keys(new_attrs_tuple, new_opt_attrs)

    type.__setattr__(cls, '_required_attributes_and_types', new_attrs_tuple)
    type.__setattr__(cls, '_required_attribute_keys', new_req_keys)
    type.__setattr__(cls, '_optional_attributes_and_defaults', new_opt_attrs)
    type.__setattr__(cls, '_ordered_keys', new_ordered_keys)

    new_req_attrs_dict = {k: v for k, v in new_attrs_tuple if k in new_req_keys}
    type.__setattr__(cls, '_defined_required_attributes', new_req_attrs_dict)
    type.__setattr__(cls, '_defined_optional_attributes', new_opt_attrs)
    type.__setattr__(cls, '_defined_keys', set(new_ordered_keys))

    if hasattr(cls, '_all_possible_keys'):
        type.__setattr__(cls, '_all_possible_keys', set(new_ordered_keys))

    _attach_model_attrs(cls, getattr(cls, 'extends', ()))

def _to_json(obj):
    """
    Helper method to recursively convert an object to a JSON-serializable dictionary.
    """
    from typed.mods.models import MODEL, LAZY_MODEL
    json_dict = {}
    for key, value in obj.__dict__.items():
        if key.startswith('_'):
            continue
        if value in MODEL or value in LAZY_MODEL:
            json_dict[key] = _to_json(value)
        elif isinstance(value, list) and all(item in MODEL or item in LAZY_MODEL for item in value):
            json_dict[key] = [_to_json(item) for item in value]
        elif isinstance(value, dict) and any(item in MODEL or item in LAZY_MODEL for item in value.values()):
            processed_dict = {}
            for sub_key, sub_value in value.items():
                if sub_value in MODEL or sub_value in LAZY_MODEL:
                    processed_dict[sub_key] = _to_json(sub_value)
                else:
                    processed_dict[sub_key] = sub_value
            json_dict[key] = processed_dict
        else:
            try:
                json.dumps(value)
                json_dict[key] = value
            except TypeError:
                json_dict[key] = str(value)

    return json_dict

def _model_to_json(model_cls):
    """
    Return a JSON-like description of a model, not a model instance.
    """
    model_cls = _materialize_if_lazy(model_cls)

    data = {}
    attrs = getattr(model_cls, 'attrs', None)
    opt   = getattr(model_cls, 'optional_attrs', None)
    mand  = getattr(model_cls, 'mandatory_attrs', None)

    if attrs is not None:
        data['attrs'] = attrs
    if opt is not None:
        data['optional_attrs'] = opt
    if mand is not None:
        data['mandatory_attrs'] = mand

    return data

def _canonical_model_key(kind, extends, conditions, attrs):
    extends_key = tuple(extends or ())
    conditions_key = tuple(conditions or ())
    attrs_key = tuple(sorted(attrs.items(), key=lambda kv: kv[0]))
    return (kind, extends_key, conditions_key, attrs_key)

def _lazy_model(
    original_cls,
    *,
    builder,
    is_exact=False,
    is_ordered=False,
    is_rigid=False,
    is_optional=False,
    is_mandatory=False,
    extends=(),
):
    name = original_cls.__name__

    namespace = {
        '__module__': original_cls.__module__,
        '__doc__':    original_cls.__doc__,
        '__builder__': staticmethod(builder),
        'is_lazy': True,
        'is_model': True,
        'is_exact': is_exact,
        'is_ordered': is_ordered,
        'is_rigid': is_rigid,
        'is_optional': is_optional,
        'is_mandatory': is_mandatory,
        '__lazy_extends__': tuple(extends),
    }

    if is_optional:
        namespace['_required_attribute_keys'] = set()
    if is_mandatory:
        namespace['_optional_attributes_and_defaults'] = {}

    from typed.mods.meta.models import LAZY_META
    LazyCls = LAZY_META(name, tuple(extends), namespace)
    LazyCls.__qualname__ = original_cls.__qualname__
    LazyCls.__display__ = 'LazyModel'
    return LazyCls

def _lazy_submodel(subclass, cls):
    if subclass is cls:
        return True

    visited = set()
    stack = [subclass]

    while stack:
        cur = stack.pop()
        if cur in visited:
            continue
        visited.add(cur)

        bases = getattr(cur, '__bases__', ())
        for base in bases:
            if base is cls:
                return True
            stack.append(base)

    return False
