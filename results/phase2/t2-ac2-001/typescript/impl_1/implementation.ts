function bfs(graph: Record<number, number[]>, start: number): number[] {
    const visited = new Set<number>();
    const queue: number[] = [start];
    const visited_order: number[] = [];
    
    while (queue.length > 0) {
        const node = queue.shift()!;
        
        if (!visited.has(node)) {
            visited.add(node);
            visited_order.push(node);
            
            const neighbors = graph[node] || [];
            for (const neighbor of neighbors) {
                if (!visited.has(neighbor) && !queue.includes(neighbor)) {
                    queue.push(neighbor);
                }
            }
        }
    }
    
    return visited_order;
}