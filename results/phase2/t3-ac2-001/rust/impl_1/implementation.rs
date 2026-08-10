use std::cmp::max;

pub struct Node {
    pub key: i32,
    pub left: Option<Box<Node>>,
    pub right: Option<Box<Node>>,
    pub height: i32,
}

fn height(node: &Option<Box<Node>>) -> i32 {
    node.as_ref().map_or(0, |n| n.height)
}

fn rotate_right(mut y: Box<Node>) -> Box<Node> {
    let mut x = y.left.take().unwrap();
    let t2 = x.right.take();
    y.left = t2;
    x.right = Some(Box::new(y));
    y.height = 1 + max(height(&y.left), height(&y.right));
    x.height = 1 + max(height(&x.left), height(&x.right));
    x
}

fn rotate_left(mut x: Box<Node>) -> Box<Node> {
    let mut y = x.right.take().unwrap();
    let t2 = y.left.take();
    x.right = t2;
    y.left = Some(Box::new(x));
    x.height = 1 + max(height(&x.left), height(&x.right));
    y.height = 1 + max(height(&y.left), height(&y.right));
    y
}

fn insert(node: Option<Box<Node>>, key: i32) -> Box<Node> {
    match node {
        None => Box::new(Node {
            key,
            left: None,
            right: None,
            height: 1,
        }),
        Some(mut n) => {
            if key < n.key {
                n.left = Some(insert(n.left, key));
            } else if key > n.key {
                n.right = Some(insert(n.right, key));
            } else {
                return n;
            }
            n.height = 1 + max(height(&n.left), height(&n.right));
            let balance = height(&n.left) - height(&n.right);

            if balance > 1 && key < n.left.as_ref().unwrap().key {
                return rotate_right(n);
            }
            if balance < -1 && key > n.right.as_ref().unwrap().key {
                return rotate_left(n);
            }
            if balance > 1 && key > n.left.as_ref().unwrap().key {
                let mut left_child = n.left.take().unwrap();
                left_child = rotate_left(left_child);
                n.left = Some(left_child);
                return rotate_right(n);
            }
            if balance < -1 && key < n.right.as_ref().unwrap().key {
                let mut right_child = n.right.take().unwrap();
                right_child = rotate_right(right_child);
                n.right = Some(right_child);
                return rotate_left(n);