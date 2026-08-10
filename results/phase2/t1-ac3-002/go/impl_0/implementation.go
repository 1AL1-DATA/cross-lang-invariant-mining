package main

func fibonacci(n int) int {
    if n == 0 {
        return 0
    }
    prev, curr := 0, 1
    for i := 1; i < n; i++ {
        prev, curr = curr, prev+curr
    }
    return curr
}