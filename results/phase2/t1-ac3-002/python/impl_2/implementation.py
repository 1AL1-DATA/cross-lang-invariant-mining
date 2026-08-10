def fibonacci_iterative(n: int) -> int:
    """Return the nth Fibonacci number iteratively."""
    if n == 0:
        return 0
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a