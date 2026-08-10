from collections import deque

def bfs(graph, start):
    if start not in graph and not any(start in neighbors for neighbors in graph.values()):
        return [start]
    
    visited = set()
    visited_order = []
    queue = deque([start])
    visited.add(start)
    
    while queue:
        node = queue.popleft()
        visited_order.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return visited_order