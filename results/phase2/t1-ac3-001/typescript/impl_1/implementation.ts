function factorial(n: number): number {
    if (n < 0) {
        throw new Error("n must be non-negative");
    }
    if (n > 20) {
        throw new Error("n must be at most 20");
    }
    
    let result = 1;
    for (let i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}