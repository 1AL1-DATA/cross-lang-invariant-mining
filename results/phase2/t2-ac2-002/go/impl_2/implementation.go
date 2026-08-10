package main

func DFSIterative(graph map[int][]int, start int) []int {
    visited := make(map[int]bool)
    visited_order := []int{}
    stack := []int{start}
    
    for len(stack) > 0 {
        node := stack[len(stack)-1]
        stack = stack[:len(stack)-1]
        
        if visited[node] {
            continue
        }
        
        visited[node] = true
        visited_order = append(visited_order, node)
        
        neighbors := graph[node]
        for i := len(neighbors) - 1; i >= 0; i-- {
            stack = append(stack, neighbors[i])
        }
    }
    
    return visited_order
}