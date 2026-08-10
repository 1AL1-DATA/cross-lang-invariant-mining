package main

func filterMapReduce(lst []int) int {
	result := 0
	for _, n := range lst {
		if n > 0 {
			result += n * n
		}
	}
	return result
}