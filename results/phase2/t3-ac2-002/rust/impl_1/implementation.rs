use std::collections::VecDeque;

#[derive(Debug, PartialEq, Eq)]
pub struct TreeNode {
    pub val: i32,
    pub left: Option<Box<TreeNode>>,
    pub right: Option<Box<TreeNode>>,
}

impl TreeNode {
    pub fn new(val: i32) -> Self {
        TreeNode {
            val,
            left: None,
            right: None,
        }
    }
}

pub fn level_order(root: Option<Box<TreeNode>>) -> Vec<Vec<i32>> {
    let mut result = Vec::new();
    let mut queue: VecDeque<Option<Box<TreeNode>>> = VecDeque::new();
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