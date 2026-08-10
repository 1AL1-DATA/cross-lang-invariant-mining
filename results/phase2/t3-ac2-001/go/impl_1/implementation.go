package main

type Node struct {
    Key    int
    Height int
    Left   *Node
    Right  *Node
}

func getHeight(n *Node) int {
    if n == nil {
        return -1
    }
    return n.Height
}

func updateHeight(n *Node) {
    if n == nil {
        return
    }
    leftH := getHeight(n.Left)
    rightH := getHeight(n.Right)
    if leftH > rightH {
        n.Height = leftH + 1
    } else {
        n.Height = rightH + 1
    }
}

func getBalance(n *Node) int {
    if n == nil {
        return 0
    }
    return getHeight(n.Left) - getHeight(n.Right)
}

func rotateRight(y *Node) *Node {
    x := y.Left
    t2 := x.Right

    x.Right = y
    y.Left = t2

    updateHeight(y)
    updateHeight(x)

    return x
}

func rotateLeft(x *Node) *Node {
    y := x.Right
    t2 := y.Left

    y.Left = x
    x.Right = t2

    updateHeight(x)
    updateHeight(y)

    return y
}

func rebalance(n *Node) *Node {
    if n == nil {
        return n
    }

    balance := getBalance(n)

    // Left Heavy
    if balance > 1 {
        // LL Case
        if getBalance(n.Left) >= 0 {
            return rotateRight(n)
        }
        // LR Case
        n.Left = rotateLeft(n.Left)
        return rotateRight(n)
    }

    // Right Heavy
    if balance < -1 {
        // RR Case
        if getBalance(n.Right) <= 0 {
            return rotateLeft(n)
        }
        // RL Case
        n.Right = rotateRight(n.Right)
        return rotateLeft(n)
    }

    return n
}

func Insert(root *Node, key int) *Node {
    if root == nil {
        return &Node{Key: key, Height: 0}
    }

    if key < root.Key {
        root.Left = Insert(root.Left, key)
    } else if key > root.Key {
        root.Right = Insert(root.Right, key)
    } else {
        return root
    }

    updateHeight(root)
    return rebalance(root)
}

func InOrderHeights(root *Node) []int {
    var result []int
    inorderRecursive(root, &result)
    return result
}

func inorderRecursive(n *Node, heights *[]int) {
    if n == nil {
        return
    }
    inorderRecursive(n.Left, heights)
    *heights = append(*heights, n.Height)
    inorderRecursive(n.Right, heights)
}

func Search(root *Node, key int) *Node {
    if root == nil {
        return nil
    }
    if key < root.Key {
        return Search(root.Left, key)
    }
    if key > root.Key {
        return Search(root.Right, key)
    }
    return root
}