package factorial

func Factorial(n int) int {
	if n < 0 || n > 20 {
		panic("n must be between 0 and 20 inclusive")
	}
	result := 1
	for i := 2; i <= n; i++ {
		result *= i
	}
	return result
}