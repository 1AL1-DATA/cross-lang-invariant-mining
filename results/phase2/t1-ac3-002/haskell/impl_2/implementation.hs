fib :: Int -> Int
fib n = go 0 1 n
  where
    go a _ 0 = a
    go a b i = go b (a + b) (i - 1)