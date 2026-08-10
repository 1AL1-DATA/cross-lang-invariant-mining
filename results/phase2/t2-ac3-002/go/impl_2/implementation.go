package lcs

func longestCommonSubsequence(s1, s2 string) int {
	m, n := len(s1), len(s2)
	if m == 0 || n == 0 {
		return 0
	}

	prev := make([]int, n+1)

	for i := 1; i <= m; i++ {
		curr := make([]int, n+1)
		for j := 1; j <= n; j++ {
			if s1[i-1] == s2[j-1] {
				curr[j] = prev[j-1] + 1
			} else if prev[j] > curr[j-1] {
				curr[j] = prev[j]
			} else {
				curr[j] = curr[j-1]
			}
		}
		prev = curr
	}

	return prev[n]
}