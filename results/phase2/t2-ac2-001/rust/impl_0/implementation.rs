use std::collections::{HashMap, HashSet, VecDeque};

pub fn breadth_first_search(graph: HashMap<i32, Vec<i32>>, start: i32) -> Vec<i32> {
    if !graph.contains_key(&start) {
        return vec![start];
    }
    
    let mut visited = HashSet::new();
    let mut queue = VecDeque::new();
    let mut visited_order = Vec::new();
    
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