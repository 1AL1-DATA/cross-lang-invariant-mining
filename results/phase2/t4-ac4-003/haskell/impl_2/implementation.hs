composeN :: [a -> a] -> a -> a
composeN funcs x = foldl (flip (.)) id funcs x