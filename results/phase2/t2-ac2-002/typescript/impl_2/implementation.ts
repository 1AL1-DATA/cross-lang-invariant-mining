function dfs_iterative(graph: Record<number, number[]>, start: number): number[] {
    const visited_order: number[] = [];
    const visited = new