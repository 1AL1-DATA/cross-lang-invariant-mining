use std::collections::VecDeque;

#[derive(Debug, PartialEq, Eq)]
pub struct Node {
    pub val: i32,
    pub left: Option<Box<Node>>,
    pub right: Option<Box<Node>>,
}

impl Node {
    pub fn new(val: i32) -> Self {
        Node { val, left: None, right: None }
    }
}

pub fn level_order_traversal(root: Option<Box<Node>>) -> Vec<Vec<i32>> {
    let mut result = Vec::new();
    let mut queue = VecDeque::new();

    if root.is_none() {
        return result;
    }

    queue.push_back(root.unwrap());

    while !queue.is_empty() {
        let level_size = queue.len();
        let mut level_vals = Vec::new();

        for _ in 0..level_size {
            let node = queue.pop_front().unwrap();
            let node = *node;
            level_vals.push(node.val);

            if let Some(left) = node.left {
                queue.push_back(left);
            }
            if let Some(right) = node.right {
                queue.push_back(right);
            }
        }

        result.push(level_vals);
    }

    result
}