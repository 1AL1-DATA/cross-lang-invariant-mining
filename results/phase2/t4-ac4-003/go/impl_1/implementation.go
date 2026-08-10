package main

type F func(int) int

func Compose(funcs []F, x int) int {
	result := x
	for _, f := range funcs {
		result = f(result)
	}
	return result
}