function filterMapReduce(lst: number[]): number {
    return lst
        .filter(x => x > 0)
        .map(x => x * x)
        .reduce((acc, val) => acc + val, 0);
}