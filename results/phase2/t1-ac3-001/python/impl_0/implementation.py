def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n > 20:
        raise ValueError("n must be at most 20 to avoid overflow")
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result