use std::collections::{HashMap, HashSet};

pub fn dfs_iterative(graph: HashMap<usize, Vec<usize>>, start: usize) -> Vec<usize> {
    let mut visited = HashSet::new();
    let mut stack = vec![start];
    let mut visited_order = Vec::new();

    while let Some(node) = stack.pop() {
        if visited.contains(&node) {
            continue;
        }

        visited.insert(node);
        visited_order.push(node);

        if let Some(neighbors) = graph.get(&node) {
            for &neighbor in neighbors.iter().rev() {
                if !visited.contains(&neighbor) {
                    stack.push(neighbor);
                }
            }
        }
    }

    visited_order
}