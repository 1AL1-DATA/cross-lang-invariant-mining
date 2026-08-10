data Tree a = Empty | Node a (Tree a) (Tree a)
  deriving (Show, Eq)

levelOrder :: Tree a -> [[a]]
levelOrder Empty = []
levelOrder root = go [root]
  where
    go [] = []
    go currentLevel =
        let vals = [v | Node v _ _ <- currentLevel]
            nextLevel = concatMap children currentLevel
        in vals : go nextLevel
    children (Node _ l r) = filter (/= Empty) [l, r]