class Node:
    __slots__ = ('key', 'left', 'right', 'height')
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 0

def _height(node):
    return node.height if node else -1

def _update_height(node):
    node.height = 1 + max(_height(node.left), _height(node.right))

def _balance(node):
    return _height(node.left) - _height(node.right)

def _rotate_right(y):
    x = y.left
    T2 = x.right
    x.right = y
    y.left = T2
    _update_height(y)
    _update_height(x)
    return x

def _rotate_left(x):
    y = x.right
    T2 = y.left
    y.left = x
    x.right = T2
    _update_height(x)
    _update_height(y)
    return y

def _insert(node, key):
    if node is None:
        return Node(key)
    if key < node.key:
        node.left = _insert(node.left, key)
    elif key > node.key:
        node.right = _insert(node.right, key)
    else:
        # Key already present – nothing to change
        return node
    _update_height(node)
    bal = _balance(node)

    if bal > 1:
        if key < node.left.key:
            # LL rotation
            return _rotate_right(node)
        else:
            # LR rotation
            node.left = _rotate_left(node.left)
            return _rotate_right(node)
    if bal < -1:
        if key > node.right.key:
            # RR rotation
            return _rotate_left(node)
        else:
            # RL rotation
            node.right = _rotate_right(node.right)
            return _rotate_left(node)
    return node

def _inorder_heights(node, heights):
    if node:
        _inorder_heights(node.left, heights)
        heights.append(node.height)
        _inorder_heights(node.right, heights)

def search(node, key):
    while node:
        if key == node.key:
            return True
        elif key < node.key:
            node = node.left
        else:
            node = node.right
    return False

def avl_insert(keys):
    root = None
    for k in keys:
        root = _insert(root, k)
    heights = []
    _inorder_heights(root, heights)
    return root, heights