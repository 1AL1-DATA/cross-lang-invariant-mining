package main

import "fmt"

// Node represents a node in the AVL tree
type Node struct {
	Key    int
	Height int
	Left   *Node
	Right  *Node
}

// NewNode creates a new AVL tree node
func NewNode(key int) *Node {
	return &Node{
		Key:    key,
		Height: 1,
		Left:   nil,
		Right:  nil,
	}
}

// GetHeight returns the height of a node (0 for nil nodes)
func GetHeight(n *Node) int {
	if n == nil {
		return 0
	}
	return n.Height
}

// GetBalance returns the balance factor of a node
func GetBalance(n *Node) int {
	if n == nil {
		return 0
	}
	return GetHeight(n.Left) - GetHeight(n.Right)
}

// RightRotate performs right rotation to balance LL case
func RightRotate(y *Node) *Node {
	x := y.Left
	T2 := x.Right

	x.Right = y
	y.Left = T2

	y.Height = max(GetHeight(y.Left), GetHeight(y.Right)) + 1
	x.Height = max(GetHeight(x.Left), GetHeight(x.Right)) + 1

	return x
}

// LeftRotate performs left rotation to balance RR case
func LeftRotate(x *Node) *Node {
	y := x.Right
	T2 := y.Left

	y.Left = x
	x.Right = T2

	x.Height = max(GetHeight(x.Left), GetHeight(x.Right)) + 1
	y.Height = max(GetHeight(y.Left), GetHeight(y.Right)) + 1

	return y
}

// Insert inserts a key into the AVL tree and returns the (potentially rebalanced) root
func Insert(root *Node, key int) *Node {
	if root == nil {
		return NewNode(key)
	}

	if key < root.Key {
		root.Left = Insert(root.Left, key)
	} else if key > root.Key {
		root.Right = Insert(root.Right, key)
	} else {
		return root
	}

	root.Height = 1 + max(GetHeight(root.Left), GetHeight(root.Right))
	balance := GetBalance(root)

	if balance > 1 && key < root.Left.Key {
		return RightRotate(root)
	}
	if balance < -1 && key > root.Right.Key {
		return LeftRotate(root)
	}
	if balance > 1 && key > root.Left.Key {
		root.Left = LeftRotate(root.Left)
		return RightRotate(root)
	}
	if balance < -1 && key < root.Right.Key {
		root.Right = RightRotate(root.Right)
		return LeftRotate(root)
	}

	return root
}

// InsertAll inserts all keys into the AVL tree and returns the root
func InsertAll(keys []int) *Node {
	var root *Node
	for _, key := range keys {
		root = Insert(root, key)
	}
	return root
}

// InOrderHeights returns the in-order traversal of node heights
func InOrderHeights(root *Node) []int {
	var heights []int
	if root == nil {
		return heights
	}
	heights = append(heights, InOrderHeights(root.Left)...)
	heights = append(heights, root.Height)
	heights = append(heights, InOrderHeights(root.Right)...)
	return heights