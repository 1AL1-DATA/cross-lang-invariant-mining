pub fn compose(funcs: Vec<Box<dyn Fn(i32) -> i32>>, x: i32) -> i32 {
    funcs.into_iter().fold(x, |acc, f| f(acc))
}