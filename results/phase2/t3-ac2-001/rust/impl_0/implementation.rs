use std::cmp::max;

#[derive(Debug, Clone)]
pub struct Node {
    pub key: i32,
    pub height: i32,
    pub left: Option<Box<Node>>,
    pub right: Option<Box<Node>>,
}

impl Node {
    fn new(key: i32) -> Self {
        Node {
            key,
            height: 1,
            left: None,
            right: None,
        }
    }

    fn height(node: &Option<Box<Node>>) -> i32 {
        match node {
            None => 0,
            Some(n) => n.height,
        }
    }

    fn update_height(&mut self) {
        self.height = 1 + max(Self::height(&self.left), Self::height(&self.right));
    }

    fn get_balance(&self) -> i32 {
        Self::height(&self.left) - Self::height(&self.right)
    }

    fn right_rotate(y: Box<Node>) -> Box<Node> {
        let mut y = y;
        let x = y.left.take().unwrap();
        let t2 = x.right.take();

        x.right = Some(Box::new(y));
        let y_node = x.right.as_mut().unwrap();
        y_node.left = t2;
        y_node.update_height();

        x.height = 1 + max(Self::height(&x.left), Self::height(&x.right));
        x
    }

    fn left_rotate(x: Box<Node>) -> Box<Node> {
        let mut x = x;
        let y = x.right.take().unwrap();
        let t2 = y.left.take();

        y.left = Some(Box::new(x));
        let x_node = y.left.as_mut().unwrap();
        x_node.right = t2;
        x_node.update_height();

        y.height = 1 + max(Self::height(&y.left), Self::height(&y.right));
        y
    }

    pub fn insert(root: Option<Box<Node>>, key: i32) -> Option<Box<Node>> {
        let mut node = match root {
            Some(n) => n,
            None => return Some(Box::new(Self::new(key))),
        };

        if key < node.key {
            node.left = Self::insert(node.left, key);
        } else if key > node.key {
            node.right = Self::insert(node.right, key);
        } else {
            return Some(node);
        }

        node.update_height();

        let balance = node.get_balance();

        if balance > 1 && key < node.left.as_ref().unwrap().key {
            return Some(Self::right_rotate(node));
        }

        if balance < -1 && key > node.right.as_ref().unwrap().key {
            return Some(Self::left_rotate(node));
        }

        if balance > 1 && key > node.left.as_ref().unwrap().key {
            node.left = Some(Self::left_rotate(node.left.take().unwrap()));
            return Some(Self::right_rotate(node));
        }

        if balance < -1 && key < node.right.as_ref().unwrap().key {
            node.right = Some(Self::right_rotate(node.right.take().unwrap()));
            return Some(Self::left_rotate(node));
        }

        Some(node)
    }

    pub fn search(root: &Option<Box<Node>>, key: i32) -> Option<i32> {
        let mut current = root;
        while let Some(node) = current {
            if key == node.key {
                return Some(node.key);
            } else if key < node.key {
                current = &node.left;
            } else {
                current = &node.right;
            }
        }
        None
    }

    fn in_order_heights(node: &Option<Box<Node>>, result: &mut Vec<i32>) {
        if let Some(n) = node {
            Self::in_order_heights(&n.left, result);
            result.push(n.height);
            Self::in_order_heights(&n.right, result);
        }
    }

    pub fn get_in_order_heights(root: &Option<Box<Node>>) -> Vec<i32> {
        let mut result = Vec::new();
        Self::in_order_heights(root, &mut result);
        result
    }
}

pub fn avl_tree_insert(keys: Vec<i32>) -> (Option<Node>, Vec<i32>) {
    let mut root = None;