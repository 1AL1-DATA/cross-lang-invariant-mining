package solution

func depthFirstSearch(graph map[int][]int, start int) []int {
	visited := make(map[int]bool)
	visitedOrder := []int{}
	stack := []int{start}

	for len(stack) > 0 {
		node := stack[len(stack)-1]
		stack = stack[:len(stack)-1]

		if visited[node] {
			continue
		}

		visited[node] = true
		visitedOrder = append(visitedOrder, node)

		neighbors := graph[node]
		for i := len(neighbors) - 1; i >= 0; i-- {
			if !visited[neighbors[i]] {
				stack = append(stack, neighbors[i])
			}
		}
	}

	return visitedOrder
}