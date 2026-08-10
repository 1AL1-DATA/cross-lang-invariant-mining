function bfs(graph: Record<number, number[]>, start: number): number[] {
    const visited: Set<number> = new Set();
    const queue: number[] = [start];
    const visited_order: number[] = [];

    visited.add(start);

    while (queue.length > 0) {
        const node = queue.shift()!;
        visited_order.push(node);

        const neighbors = graph[node] || [];
        for (const neighbor of neighbors) {
            if (!visited.has(neighbor)) {
                visited.add(neighbor);
                queue.push(neighbor);
            }
        }
    }

    return visited_order;
}