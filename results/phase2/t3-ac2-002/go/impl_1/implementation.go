package main

type Node struct {
	Val   int
	Left  *Node
	Right *Node
}

func levelOrder(root *Node) [][]int {
	if root == nil {
		return [][]int{}
	}

	result := [][]int{}
	queue := []*Node{root}

	for len(queue) > 0 {
		levelSize := len(queue)
		level := make([]int, 0, levelSize)

		for i := 0; i < levelSize; i++ {
			node := queue[0]
			queue = queue[1:]
			level = append(level, node.Val)

			if node.Left != nil {
				queue = append(queue, node.Left)
			}
			if node.Right != nil {
				queue = append(queue, node.Right)
			}
		}

		result = append(result, level)
	}

	return result
}