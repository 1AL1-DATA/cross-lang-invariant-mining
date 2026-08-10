lcsLength :: String -> String -> Int
lcsLength s1 s2 = dp !! m !! n
  where
    m = length s1
    n = length s2
    dp = [[if i == 0 || j == 0 
           then 0 
           else if s1 !! (i - 1) == s2 !! (j - 1) 
                then dp !! (i - 1) !! (j - 1) + 1 
                else max (dp !! (i - 1) !! j) (dp !! i !! (j - 1))
           | j <- [0..n]]
          | i <- [0..m]]