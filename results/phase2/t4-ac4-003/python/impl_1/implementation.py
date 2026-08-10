def compose_n_functions(funcs, x):
    result = x
    for func in funcs:
        result = func(result)
    return result