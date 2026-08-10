def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    """
    Solve the 0/1 knapsack problem using dynamic programming.

    Parameters
    ----------
    weights : list[int]
        Weights of the items.
    values : list[int]
        Values of the items.
    capacity : int
        Maximum capacity of the knapsack.

    Returns
    -------
    int
        Maximum total value achievable.
    """
    n = len(weights)
    if n != len(values):
        raise ValueError("weights and values must have the same length")
    if n == 0 or capacity <= 0:
        return 0

    # 1‑D DP array: dp[c] = max value for capacity c
    dp = [0] * (capacity + 1)

    for w, v in zip(weights, values):
        if w > capacity:
            # Item alone exceeds capacity, cannot be taken
            continue
        # Update backwards to ensure each item is used at most once
        for c in range(capacity, w - 1, -1):
            candidate = dp[c - w] + v
            if candidate > dp[c]:
                dp[c] = candidate

    return dp[capacity]