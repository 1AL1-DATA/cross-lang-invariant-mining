package main

func longestCommonSubsequence(s1 string, s2 string) int {
	m := len(s1)
	n := len(s2)

	if m == 0 || n == 0 {
		return 0
	}

	prev := make([]int, n+1)
	curr := make([]int, n+1)

	for i := 1; i <= m; i++ {
		for j := 1; j <= n; j++ {
			if s1[i-1] == s2[j-1] {
				curr[j] = prev[j-1] + 1
			} else {
				if prev[j] > curr[j-1] {
					curr[j] = prev[j]
				} else {
					curr[j] = curr[j-1]
				}
			}
		}
		prev, curr = curr, prev
	}

	return prev[n]
}