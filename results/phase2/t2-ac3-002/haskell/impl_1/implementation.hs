lcs :: String -> String -> Int
lcs [] _ = 0
lcs _ [] = 0
lcs s1 s2 = dp !! n1 !! n2
  where
    n1 = length s1
    n2 = length s2
    dp = [[ if i == 0 || j == 0 
            then 0 
            else if s1 !! (i-1) == s2 !! (j-1) 
                 then dp !! (i-1) !! (j-1) + 1 
                 else max (dp !! (i-1) !! j) (dp !! i !! (j-1))
            | j <- [0..n2] ] 
          | i <- [0..n1] ]