use std::collections::{HashMap, HashSet, VecDeque};

pub fn bfs(graph: &HashMap<usize, Vec<usize>>, start: usize) -> Vec<usize> {
    let mut visited_order = Vec::new();
    let mut visited = HashSet::new();
    let mut queue = VecDeque::new();
    
    queue.push_back(start);
    visited.insert(start);
    
    while let Some(node) = queue.pop_front() {
        visited_order.push(node);
        
        if let Some(neighbors) = graph.get(&node) {
            for &neighbor in neighbors {
                if !visited.contains(&neighbor) {
                    visited.insert(neighbor);
                    queue.push_back(neighbor);
                }
            }
        }
    }
    
    visited_order
}