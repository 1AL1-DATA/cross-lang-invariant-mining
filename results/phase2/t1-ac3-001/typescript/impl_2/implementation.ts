function factorial(n: number): number {
    if (n < 0 || n > 20) {
        throw new Error("n must be between 0 and 20");
    }
    
    let result = 1;
    for (let i = 2; i <= n; i++) {
        result *= i;
    }
    
    return result;
}