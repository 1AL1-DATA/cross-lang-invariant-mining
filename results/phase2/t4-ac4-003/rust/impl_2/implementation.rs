fn compose_n_functions(funcs: &[impl Fn(i32) -> i32], x: i32) -> i32 {
    let mut result = x;
    for f in funcs {
        result = f(result);
    }
    result
}