fn compose_n_functions<F>(funcs: &[F], x: i32) -> i32
where
    F: Fn(i32) -> i32,
{
    fn apply<F>(acc: i32, f: &F) -> i32
    where
        F: Fn(i32) -> i32,
    {
        f(acc)
    }
    funcs.iter().fold(x, apply)
}