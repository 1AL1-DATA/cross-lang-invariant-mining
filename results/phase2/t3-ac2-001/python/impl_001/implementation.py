def solution(root):
    if root is None: return 0
    return 1 + max(solution(root.left), solution(root.right))
