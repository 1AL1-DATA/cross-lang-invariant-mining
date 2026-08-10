pub fn solution(root: Option<Box<TreeNode>>) -> i32 {
    match root {
        None => 0,
        Some(n) => 1 + solution(n.left).max(solution(n.right))
    }
}
