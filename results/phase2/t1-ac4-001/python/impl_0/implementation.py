def flatten_a_list(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten_a_list(item))
        else:
            result.append(item)
    return result