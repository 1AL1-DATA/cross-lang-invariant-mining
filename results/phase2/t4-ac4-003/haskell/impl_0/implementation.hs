composeN :: [a -> a] -> a -> a
composeN = foldl (flip ($))