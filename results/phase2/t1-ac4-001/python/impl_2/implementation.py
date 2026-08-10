def flatten(lst):
    """Flatten a list that may contain nested lists."""
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result