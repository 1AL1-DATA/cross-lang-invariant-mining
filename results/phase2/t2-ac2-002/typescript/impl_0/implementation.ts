function depthFirstSearch(graph: Record<number, number[]>, start: number): number[] {
    const visited: Set<number> = new Set();
    const visitedOrder: number[] = [];
    const stack: number[] = [start];
    
    while (stack.length > 0) {
        const node = stack.pop()!;
        
        if (!visited.has(node)) {
            visited.add(node);
            visitedOrder.push(node);
            
            const neighbors = graph[node] || [];
            for (let i = neighbors.length - 1; i >= 0; i--) {
                const neighbor = neighbors[i];
                if (!visited.has(neighbor)) {
                    stack.push(neighbor);
                }
            }
        }
    }
    
    return visitedOrder;
}