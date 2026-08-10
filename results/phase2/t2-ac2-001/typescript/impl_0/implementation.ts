export function bfs(graph: Record<number, number[]>, start: number): number[] {
    const visited = new Set<number>();
    const visitedOrder: number[] = [];
    const queue: number[] = [start];
    visited.add(start);
    
    while (queue.length > 0) {
        const node = queue.shift()!;
        visitedOrder.push(node);
        
        const neighbors = graph[node] || [];
        for (const neighbor of neighbors) {
            if (!visited.has(neighbor)) {
                visited.add(neighbor);
                queue.push(neighbor);
            }
        }
    }
    
    return visitedOrder;
}