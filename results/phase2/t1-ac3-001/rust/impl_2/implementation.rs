pub fn factorial(n: i32) -> u64 {
    if n < 0 || n > 20 {
        panic!("n must be between 0 and 20 inclusive");
    }
    let mut result: u64 = 1;
    for i in 1..=n as u64 {
        result *= i;
    }
    result
}