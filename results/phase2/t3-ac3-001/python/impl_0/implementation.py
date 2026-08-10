def knapsack_0_1(weights, values, capacity):
    if not weights or not values or capacity <= 0:
        return 0
    
    n = len(weights)
    if n == 0:
        return 0
    
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        weight = weights[i - 1]
        value = values[i - 1]
        for w in range(capacity + 1):
            if weight <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - weight] + value)
            else:
                dp[i][w] = dp[i - 1][w]
    
    return dp[n][capacity]