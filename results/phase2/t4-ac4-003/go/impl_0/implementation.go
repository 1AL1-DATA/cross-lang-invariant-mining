package main

func composeN(funcs []func(int) int, x int) int {
	result := x
	for _, f := range funcs {
		result = f(result)
	}
	return result
}