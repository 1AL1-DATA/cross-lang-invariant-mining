package avl

// Node represents a node in the AVL tree
type Node struct {
	Key    int
	Height int
	Left   *Node
	Right  *Node
}

// getHeight returns the height of a node (0 for nil nodes)
func getHeight(n *Node) int {
	if n == nil {
		return 0
	}
	return n.Height
}

// getBalance returns the balance factor of a node
func getBalance(n *Node) int {
	if n == nil {
		return 0
	}
	return getHeight(n.Left) - getHeight(n.Right)
}

// max returns the maximum of two integers
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// rotateRight performs a right rotation (LL case)
func rotateRight(y *Node) *Node {
	x := y.Left
	T2 := x.Right

	x.Right = y
	y.Left = T2

	y.Height = max(getHeight(y.Left), getHeight(y.Right)) + 1
	x.Height = max(getHeight(x.Left), getHeight(x.Right)) + 1

	return x
}

// rotateLeft performs a left rotation (RR case)
func rotateLeft(x *Node) *Node {
	y := x.Right
	T2 := y.Left

	y.Left = x
	x.Right = T2

	x.Height = max(getHeight(x.Left), getHeight(x.Right)) + 1
	y.Height = max(getHeight(y.Left), getHeight(y.Right)) + 1

	return y
}

// Insert inserts a key into the AVL tree and returns the root
func Insert(root *Node, key int) *Node {
	if root == nil {
		return &Node{Key: key, Height: 1}
	}

	if key < root.Key {
		root.Left = Insert(root.Left, key)
	} else if key > root.Key {
		root.Right = Insert(root.Right, key)
	} else {
		return root
	}

	root.Height = max(getHeight(root.Left), getHeight(root.Right)) + 1

	balance := getBalance(root)

	if balance > 1 && key < root.Left.Key {
		return rotateRight(root)
	}

	if balance < -1 && key > root.Right.Key {
		return rotateLeft(root)
	}

	if balance > 1 && key > root.Left.Key {
		root.Left = rotateLeft(root.Left)
		return rotateRight(root)
	}

	if balance < -1 && key < root.Right.Key {
		root.Right = rotateRight(root.Right)
		return rotateLeft(root)
	}

	return root
}

// InsertAll inserts multiple keys and returns the root
func InsertAll(keys []int) *Node {
	var root *Node
	for _, key := range keys {
		root = Insert(root, key)
	}
	return root
}

// Search searches for a key in the AVL tree
func Search(root *Node, key int) bool {
	if root == nil {
		return false
	}
	if key < root.Key {
		return Search(root.Left, key)
	}
	if key > root.Key {
		return Search(root.Right, key)
	}
	return true
}

// InOrderHeights returns in-order traversal of node heights
func InOrderHeights(root *Node) []int {
	var heights []int
	inOrderHelper(root, &heights)
	return heights
}

func inOrderHelper(n *Node, heights *[]int) {
	if n == nil {
		return
	}
	inOrderHelper(n.Left, heights)
	*heights = append(*heights, n.Height)
	inOrderHelper(n.Right, heights)
}