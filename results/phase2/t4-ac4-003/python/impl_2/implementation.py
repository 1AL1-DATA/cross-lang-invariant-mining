def compose_n_functions(funcs, x):
    result = x
    for f in funcs:
        result = f(result)
    return result