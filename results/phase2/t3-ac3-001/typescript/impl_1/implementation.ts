function knapsack(weights: number[], values: number[], capacity: number): number {
    const n = weights.length;
    
    if (n === 0 || capacity === 0) {
        return 0;
    }
    
    const dp: number[][] = Array(n + 1)
        .fill(null)
        .map(() => Array(capacity + 1).fill(0));
    
    for (let i = 1; i <= n; i++) {
        for (let w = 0; w <= capacity; w++) {
            dp[i][w] = dp[i - 1][w];
            
            if (weights[i - 1] <= w) {
                dp[i][w] = Math.max(
                    dp[i][w],
                    dp[i - 1][w - weights[i - 1]] + values[i - 1]
                );
            }
        }
    }
    
    return dp[n][capacity];
}