package bfs

func BFS(graph map[int][]int, start int) []int {
	if graph == nil {
		return []int{start}
	}

	if _, exists := graph[start]; !exists {
		return []int{start}
	}

	visited := make(map[int]bool)
	queue := []int{start}
	result := []int{}

	for len(queue) > 0 {
		node := queue[0]
		queue = queue[1:]

		if visited[node] {
			continue
		}

		visited[node] = true
		result = append(result, node)

		for _, neighbor := range graph[node] {
			if !visited[neighbor] {
				queue = append(queue, neighbor)
			}
		}
	}

	return result
}