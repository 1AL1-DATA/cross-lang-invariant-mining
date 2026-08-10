function filterMapReduce(lst: number[]): number {
    return lst
        .filter(x => x > 0)
        .map(x => x * x)
        .reduce((sum, x) => sum + x, 0);
}