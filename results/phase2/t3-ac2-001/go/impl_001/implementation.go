func Solution(root *TreeNode) int {
    if root == nil { return 0 }
    return 1 + max(Solution(root.Left), Solution(root.Right))
}
