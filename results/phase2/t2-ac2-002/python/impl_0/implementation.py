def depth_first_search_iterative(graph: dict[int, list[int]], start: int) -> list[int]:
    visited_order = []
    visited = set()
    stack = [start]

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        visited_order.append(node)

        # Push neighbors in reverse order to preserve typical DFS ordering
        for neighbor in reversed(graph.get(node, [])):
            if neighbor not in visited:
                stack.append(neighbor)

    return visited_order