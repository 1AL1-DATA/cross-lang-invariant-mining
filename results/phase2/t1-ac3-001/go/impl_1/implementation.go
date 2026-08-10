package main

import "errors"

func Factorial(n int) (int, error) {
    if n < 0 {
        return 0, errors.New("n must be non-negative")
    }
    if n > 20 {
        return 0, errors.New("n must be at most 20")
    }
    
    result := 1
    for i := 2; i <= n; i++ {
        result *= i
    }
    return result, nil
}