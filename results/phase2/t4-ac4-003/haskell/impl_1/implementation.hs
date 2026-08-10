composeN :: [a -> a] -> a -> a
composeN = foldr (.) id