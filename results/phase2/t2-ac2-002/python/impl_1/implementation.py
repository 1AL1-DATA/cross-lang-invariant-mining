from typing import List, Dict

def dfs_iterative(graph: Dict[int, List[int]], start: int) -> List[int]:
    visited_order: List[int] = []
    visited_set = set()
    stack = [start]

    while stack:
        node = stack.pop()
        if node in visited_set:
            continue
        visited_set.add(node)
        visited_order.append(node)

        # Push neighbors onto the stack. Reversing preserves the original order
        neighbors = graph.get(node, [])
        for neighbor in reversed(neighbors):
            if neighbor not in visited_set:
                stack.append(neighbor)

    return visited_order