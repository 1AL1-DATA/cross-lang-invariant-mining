use std::collections::{HashMap, HashSet};

fn depth_first_search(graph: HashMap<i32, Vec<i32>>, start: i32) -> Vec<i32> {
    let mut visited_order = Vec::new();
    let mut visited = HashSet::new();
    let mut stack = Vec::new();
    
    stack.push(start);
    
    while let Some(node) = stack.pop() {
        if !visited.contains(&node) {
            visited.insert(node);
            visited_order.push(node);
            
            if let Some(neighbors) = graph.get(&node) {
                for neighbor in neighbors.iter().rev() {
                    stack.push(*neighbor);
                }
            }
        }
    }
    
    visited_order
}