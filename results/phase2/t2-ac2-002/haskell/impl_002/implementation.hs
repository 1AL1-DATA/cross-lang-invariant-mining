solution :: Tree a -> Int
solution Leaf = 0
solution (Node _ l r) = 1 + max (solution l) (solution r)
