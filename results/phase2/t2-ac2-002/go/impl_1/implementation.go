package main

func dfsIterative(graph map[int][]int, start int) []int {
    visited := make(map[int]bool)
    stack := []int{start}
    var result []int
    
    for len(stack) > 0 {
        node := stack[len(stack)-1]
        stack = stack[:len(stack)-1]
        
        if !visited[node] {
            visited[node] = true
            result = append(result, node)
            
            neighbors := graph[node]
            for i := len(neighbors) - 1; i >= 0; i-- {
                if !visited[neighbors[i]] {
                    stack = append(stack, neighbors[i])
                }
            }
        }
    }
    
    if len(result) == 0 {
        result = append(result, start)
    }
    
    return result
}