from typed import typed, TYPE


@typed
def test(x):
    pass

print(TYPE(test))
