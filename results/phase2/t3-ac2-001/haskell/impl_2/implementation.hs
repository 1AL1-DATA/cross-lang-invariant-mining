module AVLTree where

data AVLTree a = Empty | Node a (AVLTree a) (AVLTree a)
    deriving (Show, Eq)

height :: AVLTree a -> Int
height Empty = 0
height (Node _ l r) = 1 + max (height l) (height r)

balanceFactor :: AVLTree a -> Int
balanceFactor Empty = 0
balanceFactor (Node _ l r) = height l - height r

rotateRight :: AVLTree a -> AVLTree a
rotateRight (Node x (Node y a b) c) = Node y a (Node x b c)
rotateRight t = t

rotateLeft :: AVLTree a -> AVLTree a
rotateLeft (Node x a (Node y b c)) = Node y (Node x a b) c
rotateLeft t = t

rotateLeftRight :: AVLTree a -> AVLTree a
rotateLeftRight (Node x l r) = rotateRight (Node x (rotateLeft l)