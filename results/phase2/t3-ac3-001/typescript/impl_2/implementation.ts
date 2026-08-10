function knapsack(weights: number[], values: number[], capacity: number): number {
    const n = weights.length;
    
    if (n === 0 || capacity === 0) {
        return 0;
    }
    
    const dp = new Array(capacity + 1).fill(0);
    
    for (let i = 0; i < n; i++) {
        for (let w = capacity; w >= weights[i]; w--) {
            dp[w] = Math.max(dp[w], dp[w - weights[i]] + values[i]);
        }
    }
    
    return dp[capacity];
}