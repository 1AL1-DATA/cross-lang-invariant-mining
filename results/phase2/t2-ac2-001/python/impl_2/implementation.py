from collections import deque

def breadth_first_search(graph: dict[int, list[int]], start: int) -> list[int]:
    if start not in graph:
        return [start]
    
    visited = set()
    queue = deque([start])
    visited_order = []
    
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        visited_order.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                queue.append(neighbor)
    
    return visited_order