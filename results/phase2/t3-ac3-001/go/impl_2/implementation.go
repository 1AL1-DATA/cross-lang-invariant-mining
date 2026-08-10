package knapsack

func Knapsack(weights []int, values []int, capacity int) int {
	n := len(weights)
	if n == 0 || capacity == 0 {
		return 0
	}

	dp := make([]int, capacity+1)

	for i := 0; i < n; i++ {
		for w := capacity; w >= weights[i]; w-- {
			if dp[w-weights[i]]+values[i] > dp[w] {
				dp[w] = dp[w-weights[i]] + values[i]
			}
		}
	}

	return dp[capacity]
}