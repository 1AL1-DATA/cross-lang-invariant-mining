def dfs_iterative(graph: dict[int, list[int]], start: int) -> list[int]:
    """
    Perform an iterative depth‑first search on the given graph starting at `start`.
    Returns a list of nodes in the order they are first visited.
    """
    visited_order = []
    visited = set()
    stack = [start]

    while stack:
        node = stack.pop()
        if node in visited:
            continue

        visited.add(node)
        visited_order.append(node)

        # Push neighbors in reverse order to mimic the left‑to‑right traversal
        # of a recursive DFS.
        for neighbor in reversed(graph.get(node, [])):
            if neighbor not in visited:
                stack.append(neighbor)

    return visited_order