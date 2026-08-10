data Tree a = Empty | Node a (Tree a) (Tree a)

levelOrder :: Tree a -> [[a]]
levelOrder Empty = []
levelOrder root = go [root]
  where
    go [] = []
    go nodes = values : go (children nodes)
      where
        values = [v | Node v _ _ <- nodes]
        children = concatMap childNodes
        childNodes Empty = []
        childNodes (Node _ l r) = [l, r]