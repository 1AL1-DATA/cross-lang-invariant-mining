use std::collections::VecDeque;

#[derive(Debug, PartialEq, Eq)]
pub struct Node {
    pub val: i32,
    pub left: Option<Box<Node>>,
    pub right: Option<Box<Node>>,
}

impl Node {
    pub fn new(val: i32) -> Self {
        Node {
            val,
            left: None,
            right: None,
        }
    }
}

pub fn level_order(root: Option<Box<Node>>) -> Vec<Vec<i32>> {
    let mut result = Vec::new();
    
    if root.is_none() {
        return result;
    }
    
    let mut queue: VecDeque<Option<Box<Node>>> = VecDeque::new();
    queue.push_back(root);
    
    while !queue.is_empty() {
        let level_size = queue.len();
        let mut current_level = Vec::new();
        
        for _ in 0..level_size {
            if let Some(node) = queue.pop_front().flatten() {
                current_level.push(node.val);
                queue.push_back(node.left);
                queue.push_back(node.right);
            }
        }
        
        if !current_level.is_empty() {
            result.push(current_level);
        }
    }
    
    result
}