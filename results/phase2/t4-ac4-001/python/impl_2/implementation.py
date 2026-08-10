def filter_map_reduce(lst):
    """Return the sum of squares of the positive numbers in lst."""
    return sum(x * x for x in lst if x > 0)