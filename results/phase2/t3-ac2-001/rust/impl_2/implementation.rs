use std::cmp::max;

mod avl {
    #[derive(Debug, Clone)]
    pub struct Node {
        pub key: i32,
        pub height: i32,
        pub left: Option<Box<Node>>,
        pub right: Option<Box<Node>>,
    }

    impl Node {
        pub fn new(key: i32) -> Self {
            Node {
                key,
                height: 1,
                left: None,
                right: None,
            }
        }
    }

    fn height(node: &Option<Box<Node>>) -> i32 {
        node.as_ref().map_or(0, |n| n.height)
    }

    fn update_height(node: &mut Box<Node>) {
        node.height = 1 + max(height(&node.left), height(&node.right));
    }

    fn get_balance(node: &Option<Box<Node>>) -> i32 {
        height(&node.as_ref().and_then(|n| n.left.clone()))
            - height(&node.as_ref().and_then(|n| n.right.clone()))
    }

    fn right_rotate(y: Box<Node>) -> Box<Node> {
        let mut y = y;
        let x = y.left.take().unwrap();
        let t2 = x.right.take();

        x.right = Some(Box::new(y));
        if let Some(ref mut right) = x.right {
            right.left = t2;
            update_height(right);
        }
        update_height(&mut x);

        x
    }

    fn left_rotate(x: Box<Node>) -> Box<Node> {
        let mut x = x;
        let y = x.right.take().unwrap();
        let t2 = y.left.take();

        y.left = Some(Box::new(x));
        if let Some(ref mut left) = y.left {
            left.right = t2;
            update_height(left);
        }
        update_height(&mut y);

        y
    }

    fn rebalance(mut node: Box<Node>) -> Box<Node> {
        update_height(&mut node);
        let balance = height(&node.left) - height(&node.right);

        // Left Left
        if balance > 1 && height(&node.left.as_ref().unwrap().left) >= height(&node.left.as_ref().unwrap().right) {
            return right_rotate(node);
        }
        // Left Right
        if balance > 1 && height(&node.left.as_ref().unwrap().left) < height(&node.left.as_ref().unwrap().right) {
            node.left = Some(left_rotate(node.left.take().unwrap()));
            return right_rotate(node);
        }
        // Right Right
        if balance < -1 && height(&node.right.as_ref().unwrap().right) >= height(&node.right.as_ref().unwrap().left) {
            return left_rotate(node);
        }
        // Right Left
        if balance < -1 && height(&node.right.as_ref().unwrap().right) < height(&node.right.as_ref().unwrap().left) {
            node.right = Some(right_rotate(node.right.take().unwrap()));
            return left_rotate(node);
        }

        node
    }

    pub fn insert(root: Option<Box<Node>>, key: i32) -> Option<Box<Node>> {
        match root {
            None => Some(Box::new(Node::new(key))),
            Some(mut node) => {
                if key < node.key {
                    node.left = insert(node.left, key);
                } else if key > node.key {
                    node.right = insert(node.right, key);
                } else {
                    return Some(node);
                }
                Some(rebalance(node))
            }
        }
    }

    pub fn in_order_heights(root: &Option<Box<Node>>, result: &mut Vec<i32>) {
        if let Some(node) = root {
            in_order_heights(&node.left, result);
            result.push(node.height);
            in_order_heights(&node.right, result);
        }
    }

    pub fn search(root: &Option<Box<Node>>, key: i32) -> bool {
        match root {
            None => false,
            Some(node) => {
                if key == node.key {
                    true
                } else if key < node.key {
                    search(&node.left, key)
                } else {
                    search(&node.right, key)
                }
            }
        }
    }

    pub fn avl_tree_insert(keys: Vec<i32>) -> (Option<Box<Node>>, Vec<i32>) {
        let mut root: Option<Box<Node>> = None;
        for key in keys {
            root = insert(root, key);
        }
        let mut heights = Vec::new();
        in_order_heights(&root, &mut heights);
        (root, heights)
    }
}

pub use avl::{Node, avl_tree_insert, search};