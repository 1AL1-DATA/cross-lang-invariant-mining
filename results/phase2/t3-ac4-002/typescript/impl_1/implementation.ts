function topKElements(lst: number[], k: number): number[] {
    return [...lst].sort((a, b) => b - a).slice(0, k);
}