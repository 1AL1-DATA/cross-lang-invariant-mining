pub fn factorial(n: i32) -> u64 {
    if n < 0 {
        panic!("Factorial is undefined for negative numbers");
    }
    let n = n as u32;
    if n > 20 {
        panic!("Factorial overflow: n must be <= 20");
    }
    let mut result: u64 = 1;
    for i in 1..=n {
        result *= u64::from(i);
    }
    result
}