from typed.mods.meta.factories import TUPLE, LIST, SET, DICT

Tuple = TUPLE("Tuple", (tuple,), {
    "__null__": (),
    "__display__": "Tuple",
    "__convert__": staticmethod(TUPLE.__convert__),
    "__doc__": TUPLE.__doc__
})

List = LIST("List", (list,), {
    "__null__": [],
    "__display__": "List",
    "__convert__": staticmethod(LIST.__convert__),
    "__doc__": LIST.__doc__
})

Set = SET("List", (set,), {
    "__null__": set(),
    "__display__": "Set",
    "__convert__": staticmethod(SET.__convert__),
    "__doc__": SET.__doc__
})

Dict = DICT("Dict", (dict,), {
    "__null__": {},
    "__display__": "Dict",
    "__convert__": staticmethod(DICT.__convert__),
    "__doc__": DICT.__doc__
})
