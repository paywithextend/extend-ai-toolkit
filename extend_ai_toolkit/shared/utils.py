def pop_first(iterable: list, predicate, default=None):
    for index, item in enumerate(iterable):
        if predicate(item):
            return iterable.pop(index)
    return default
