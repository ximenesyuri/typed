import re
import inspect
import ast
from functools  import wraps

def poly(arg, num_args=-1):
    """
    1. Can be used as a decorator for Typed functions (parametric, e.g. for union-branching).
    2. Can be used for method name dispatch (original purpose).
    """
    from typed.mods.helper.helper import _name
    from typed.mods.types.base import TYPE
    from typed.mods.factories.meta import ATTR

    if callable(arg):
        from typed.mods.types.func import Typed
        if not isinstance(arg, Typed):
            try:
                func = Typed(arg)
            except Exception as e:
                raise TypeErr(e)
        else:
            func = arg

        domain = func.domain
        params_info = inspect.signature(func.func).parameters

        from typed.mods.factories.base import Union as Union_factory
        union_param_names = []
        union_types_dict = {}

        for idx, (param_name, typ) in enumerate(zip(params_info.keys(), domain)):
            if _name(typ).startswith('Union('):
                types_tuple = getattr(typ, '__types__', None)
                if types_tuple:
                    union_param_names.append(param_name)
                    union_types_dict[param_name] = types_tuple

        if not union_param_names:
            raise TypeError

        try:
            src = inspect.getsource(func.func)
        except (OSError, TypeError):
            raise TypeError(f"poly-decorator cannot inspect source code for {_name(func)}; parameterized condition not checked.")

        tree = ast.parse(src)

        def check_union_branches(param, type_tuple):
            found_types = set()
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name) and node.func.id == 'isinstance'
                    and len(node.args) == 2):

                    if isinstance(node.args[0], ast.Name) and node.args[0].id == param:
                        type_arg = node.args[1]
                        if isinstance(type_arg, ast.Name):
                            found_types.add(type_arg.id)
                        elif isinstance(type_arg, ast.Attribute):
                            found_types.add(type_arg.attr)
                        elif isinstance(type_arg, ast.Tuple):
                            for elt in type_arg.elts:
                                if isinstance(elt, ast.Name):
                                    found_types.add(elt.id)
                                elif isinstance(elt, ast.Attribute):
                                    found_types.add(elt.attr)
            type_names = set(_name(t) for t in type_tuple)
            if not type_names.issubset(found_types):
                missing = type_names - found_types
                raise TypeError(
                    f"Missing checking in polymorphism '{_name(func)}':\n"
                    f" ==> '{_name(param)}': union type without instance check conditionals\n"
                    f"     [expected_checks] {', '.join(type_names)}\n"
                    f"     [missing_checks]  {', '.join(missing)}."
                )

        for p, types_tuple in union_types_dict.items():
            check_union_branches(p, types_tuple)

        return func

    from typed.mods.types.base import Str
    if isinstance(arg, Str):
        special_method = arg
        pattern = r'^__.*__$'
        if not bool(re.match(pattern, special_method)):
            raise TypeError

        base_type = ATTR(special_method)

        if num_args == 0:
            def _poly(typ):
                if not isinstance(typ, base_type):
                    return TypeError
                return getattr(type, special_method)
            return _poly

        def _poly(*args):
            if not args:
                return None

            if len(args) > 0:
                if not len(args) == num_args:
                    return ValueError

            from typed.mods.types.base import TYPE
            for arg in args:
                if not isinstance(TYPE(arg), base_type):
                    raise TypeError(
                        f"Wrong type in polymorphism '{special_method.replace('_', '')}'\n"
                        f" ==> {_name(arg)}: has an unexpected type.\n"
                        f"     [expected_type]: an instance of {_name()}\n"
                        f"     [received_type]: {_name(TYPE(arg))}"
                    )

                if not issubclass(TYPE(arg), TYPE(arg[0])):
                    raise TypeError(
                        f"Wrong type in polymorphism {special_method.replace('_', '')}\n"
                        f" ==> {_name(arg)}: has an unexpected type.\n"
                        f"     [expected_type]: a subtype of {_name(TYPE(arg[0]))}\n"
                        f"     [received_type]: {_name(TYPE(arg))}"
                    )
            try:
                method = getattr(TYPE(args[0]), special_method)
                try:
                    return method(*args)
                except Exception as e:
                    Exception(e)
            except:
                raise AttributeError(
                    f"Attribute error in {_name(args[0])}:"
                    f" ==> its type '{_name(TYPE(args[0]))}' has no attribute '{special_method}'"
                )
        return _poly

    raise TypeError(
        "Wrong type in 'poly' function:\n"
        f" ==> '{_name(arg)}': has an unexpected type\n"
         "     [expected_type] Typed or Str\n"
        f"     [received_type] {_name(TYPE(arg))}"
    )
join = poly("__join__")
