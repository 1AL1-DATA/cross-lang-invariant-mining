package main

func BreadthFirstSearch(graph map[int][]int, start int) []int {
    visited := make(map[int]bool)
    visitedOrder := []int{}
    queue := []int{start}
    
    for len(queue) > 0 {
        node := queue[0]
        queue = queue[1:]
        
        if visited[node] {
            continue
        }
        
        visited[node] = true
        visitedOrder = append(visitedOrder, node)
        
        neighbors := graph[node]
        for _, neighbor := range neighbors {
            if !visited[neighbor] {
                queue = append(queue, neighbor)
            }
        }
    }
    
    return visitedOrder
}