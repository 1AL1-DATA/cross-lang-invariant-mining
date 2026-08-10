function topKElements(lst: number[], k: number): number[] {
    return lst
        .slice()
        .sort((a, b) => b - a)
        .slice(0, k);
}