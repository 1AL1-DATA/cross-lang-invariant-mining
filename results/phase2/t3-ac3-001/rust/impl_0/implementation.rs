pub fn knapsack(weights: &[usize], values: &[usize], capacity: usize) -> usize {
    let n = weights.len();
    if n == 0 || capacity == 0 {
        return 0;
    }
    
    let mut dp = vec![0; capacity + 1];
    
    for i in 0..n {
        for w in (weights[i]..=capacity).rev() {
            dp[w] = dp[w].max(dp[w - weights[i]] + values[i]);
        }
    }
    
    dp[capacity]
}