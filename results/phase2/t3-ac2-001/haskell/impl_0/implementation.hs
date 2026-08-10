module AVLTree where

data AVLTree a = Empty | Node a (AVLTree a) (AVLTree a) deriving (Show, Eq)

height :: AVLTree a -> Int
height Empty = -1
height (Node _ l r) = 1 + max (height l) (height r)

makeNode :: a -> AVLTree a -> AVLTree a -> AVLTree a
makeNode x l r = Node x l r

balanceFactor :: AVLTree a -> Int
balanceFactor Empty = 0
balanceFactor (Node _ l r) = height l - height r

rotateRight :: AVLTree a -> AVLTree a
rotateRight (Node x (Node y a b) c) = makeNode y a (makeNode x b c)
rotateRight tree = tree

rotateLeft :: AVLTree a -> AVLTree a
rotateLeft (Node x a (Node z b c)) = makeNode z (makeNode x a b) c
rotateLeft tree = tree

rotateLeftRight :: AVLTree a -> AVLTree a
rotateLeftRight tree = rotateRight (rotateLeft tree)

rotateRightLeft :: AVLTree a -> AVLTree a
rotateRightLeft tree = rotateLeft (rotateRight tree)

rebalance :: AVLTree a -> AVLTree a
rebalance tree
    | bf > 1 && balanceFactor (leftChild tree) >= 0 = rotateRight tree
    | bf < -1 && balanceFactor (rightChild tree) <= 0 = rotateLeft tree
    | bf > 1 && balanceFactor (leftChild tree) < 0 = rotateLeftRight tree
    | bf < -1 && balanceFactor (rightChild tree) > 0 = rotateRightLeft tree
    | otherwise = tree
  where
    bf = balanceFactor tree
    leftChild (Node _ l _) = l
    rightChild (Node _ _ r) = r

insert :: Ord a => a -> AVLTree a -> AVLTree a
insert x Empty = Node x Empty Empty
insert x (Node y l r)
    | x < y     = rebalance $ Node y (insert x l) r
    | x > y     = rebalance $ Node y l (insert x r)
    | otherwise = Node y l r

inorderHeights :: AVLTree a -> [Int]
inorderHeights Empty = []
inorderHeights (Node x l r) = inorderHeights l ++ [height (Node x l r)] ++ inorderHeights r

main :: [Int] -> (AVLTree Int, [Int])
main keys = (tree, inorderHeights tree)
  where
    tree = foldr insert Empty keys