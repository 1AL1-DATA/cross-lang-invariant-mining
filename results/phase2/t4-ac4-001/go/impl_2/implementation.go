package main

func SumOfSquaresOfPositives(list []int) int {
	sum := 0
	for _, v := range list {
		if v > 0 {
			sum += v * v
		}
	}
	return sum
}