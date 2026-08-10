pub fn knapsack(weights: &[i32], values: &[i32], capacity: i32) -> i32 {
    let n = weights.len();
    if n != values.len() || capacity <= 0 || n == 0 {
        return 0;
    }
    let cap = capacity as usize;
    let mut dp = vec![0; cap + 1];
    for i in 0..n {
        let w = weights[i] as usize;
        let v = values[i];
        if w > cap {
            continue;
        }
        for j in (w..=cap).rev() {
            let candidate = dp[j - w] + v;
            if candidate > dp[j] {
                dp[j] = candidate;
            }
        }
    }
    dp[cap]
}