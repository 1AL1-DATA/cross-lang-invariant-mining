class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1


def get_height(node):
    if node is None:
        return 0
    return node.height


def update_height(node):
    if node is not None:
        node.height = max(get_height(node.left), get_height(node.right)) + 1


def get_balance(node):
    if node is None:
        return 0
    return get_height(node.left) - get_height(node.right)


def rotate_right(y):
    x = y.left
    T2 = x.right
    
    x.right = y
    y.left = T2
    
    update_height(y)
    update_height(x)
    
    return x


def rotate_left(x):
    y = x.right
    T2 = y.left
    
    y.left = x
    x.right = T2
    
    update_height(x)
    update_height(y)
    
    return y


def rebalance(node, key):
    balance = get_balance(node)
    
    # Left Left Case
    if balance > 1 and key < node.left.key:
        return rotate_right(node)
    
    # Right Right Case
    if balance < -1 and key > node.right.key:
        return rotate_left(node)
    
    # Left Right Case
    if balance > 1 and key > node.left.key:
        node.left = rotate_left(node.left)
        return rotate_right(node)
    
    # Right Left Case
    if balance < -1 and key < node.right.key:
        node.right = rotate_right(node.right)
        return rotate_left(node)
    
    return node


def insert(node, key):
    if node is None:
        return Node(key)
    
    if key < node.key:
        node.left = insert(node.left, key)
    elif key > node.key:
        node.right = insert(node.right, key)
    else:
        return node
    
    update_height(node)
    return rebalance(node, key)


def get_inorder_heights(node, result=None):
    if result is None:
        result = []
    
    if node is None:
        return result
    
    get_inorder_heights(node.left, result)
    result.append(node.height)
    get_inorder_heights(node.right, result)
    
    return result


def search(node, key):
    if node is None:
        return False
    
    if key == node.key:
        return True
    elif key < node.key:
        return search(node.left, key)
    else:
        return search(node.right, key)


def avl_tree_insert(keys):
    root = None
    
    for key in keys:
        root = insert(root, key)
    
    heights = get_inorder_heights(root)
    
    return root, heights