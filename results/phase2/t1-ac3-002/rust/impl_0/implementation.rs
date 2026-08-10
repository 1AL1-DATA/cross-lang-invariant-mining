pub fn fibonacci(n: u32) -> i32 {
    if n == 0 {
        return 0;
    }
    let mut prev = 0i32;
    let mut curr = 1i32;
    for _ in 1..n {
        let next = prev + curr;
        prev = curr;
        curr = next;
    }
    curr
}