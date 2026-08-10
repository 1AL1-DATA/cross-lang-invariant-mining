data Tree a = Empty | Node a (Tree a) (Tree a) deriving (Show, Eq)

levelOrder :: Tree a -> [[a]]
levelOrder Empty = []
levelOrder root = go [root]
  where
    go [] = []
    go currentLevel =
      let values = map valueOf currentLevel
          nextLevel = concatMap childrenOf currentLevel
      in values : go nextLevel
    
    valueOf (Node v _ _) = v
    childrenOf (Node _ l r) = filter (/= Empty) [l, r]
    childrenOf Empty = []