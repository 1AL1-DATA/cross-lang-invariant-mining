use std::collections::{HashMap, HashSet};

pub fn depth_first_search(graph: HashMap<usize, Vec<usize>>, start: usize) -> Vec<usize> {
    let mut visited = HashSet::new();
    let mut stack = vec![start];
    let mut result = Vec::new();
    
    while let Some(node) = stack.pop() {
        if !visited.contains(&node) {
            visited.insert(node);
            result.push(node);
            
            if let Some(neighbors) = graph.get(&node) {
                for &neighbor in neighbors.iter().rev() {
                    stack.push(neighbor);
                }
            }
        }
    }
    
    result
}