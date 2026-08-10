pub fn factorial(n: i64) -> i64 {
    if n < 0 || n > 20 {
        panic!("n must be between 0 and 20 inclusive");
    }
    
    let mut result: i64 = 1;
    for i in 1..=n {
        result *= i;
    }
    result
}