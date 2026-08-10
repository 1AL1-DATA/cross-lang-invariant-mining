fibonacci :: Int -> Int
fibonacci n = go n 0 1
  where
    go 0 a _ = a
    go 1 _ b = b
    go k a b = go (k - 1) b (a + b)