function dfs_iterative(graph: Record<number, number[]>, start: number): number[] {
  const visited = new Set<number>();
  const visitedOrder: number[] = [];
  const stack: number[] = [start];

  while (stack.length > 0) {
    const node = stack.pop()!;
    
    if (visited.has(node)) {
      continue;
    }
    
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

  return visitedOrder;
}