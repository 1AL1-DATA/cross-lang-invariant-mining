class Node {
    key: number;
    left: Node | null;
    right: Node | null;
    height: number;

    constructor(key: number) {
        this.key = key;
        this.left = null;
        this.right = null;
        this.height = 1;
    }
}

function getHeight(node: Node | null): number {
    return node ? node.height : 0;
}

function getBalance(node: Node | null): number {
    return node ? getHeight(node.left) - getHeight(node.right) : 0;
}

function rightRotate(y: Node): Node {
    const x = y.left!;
    const T2 = x.right;

    x.right = y;
    y.left = T2;

    y.height = Math.max(getHeight(y.left), getHeight(y.right)) + 1;
    x.height = Math.max(getHeight(x.left), getHeight(x.right)) + 1;

    return x;
}

function leftRotate(x: Node): Node {
    const y = x.right!;
    const T2 = y.left;

    y.left = x;
    x.right = T2;

    x.height = Math.max(getHeight(x.left), getHeight(x.right)) + 1;
    y.height = Math.max(getHeight(y.left), getHeight(y.right)) + 1;

    return y;
}

function insert(node: Node | null, key: number): Node {
    if (!node) {
        return new Node(key);
    }

    if (key < node.key) {
        node.left = insert(node.left, key);
    } else if (key > node.key) {
        node.right = insert(node.right, key);
    } else {
        return node;
    }

    node.height = Math.max(getHeight(node.left), getHeight(node.right)) + 1;

    const balance = getBalance(node);

    if (balance > 1 && key < node.left.key) {
        return rightRotate(node);
    }

    if (balance < -1 && key > node.right.key) {
        return leftRotate(node);
    }

    if (balance > 1 && key > node.left.key) {
        node.left = leftRotate(node.left);
        return rightRotate(node);
    }

    if (balance < -1 && key < node.right.key) {
        node.right = rightRotate(node.right);
        return leftRotate(node);
    }

    return node;
}

function search(node: Node | null, key: number): boolean {
    if (!node) {
        return false;
    }
    if (key < node.key) {
        return search(node.left, key);
    } else if (key > node.key) {
        return search(node.right, key);
    }
    return true;
}

function inOrderHeights(node: Node | null, heights: number[]): void {
    if (node !== null) {
        inOrderHeights(node.left, heights);
        heights.push(node.height);
        inOrderHeights(node.right, heights);
    }
}

export function avlTreeInsert(keys: number[]): { root: Node | null; heights: number[] } {
    let root: Node | null = null;

    for (const key of keys) {
        root = insert(root, key);
    }

    const heights: number[] = [];
    inOrderHeights(root, heights);

    return { root, heights };
}

export { Node, search, insert, getHeight, getBalance, rightRotate, leftRotate };