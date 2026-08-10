interface Node {
  val: number;
  left: Node | null;
  right: Node | null;
}

function levelOrder(root: Node | null): number[][] {
  if (!root) return [];
  
  const result: number[][] = [];
  const queue: Node[] = [root];
  
  while (queue.length > 0) {
    const levelSize = queue.length;
    const currentLevel: number[] = [];
    
    for (let i = 0; i < levelSize; i++) {
      const node = queue.shift()!;
      currentLevel.push(node.val);
      
      if (node.left) queue.push(node.left);
      if (node.right) queue.push(node.right);
    }
    
    result.push(currentLevel);
  }
  
  return result;
}