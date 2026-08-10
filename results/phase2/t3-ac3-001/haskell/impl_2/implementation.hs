knapsack :: [Int] -> [Int] -> Int -> Int
knapsack [] _ _ = 0
knapsack _ [] _ = 0
knapsack weights values capacity
  | capacity < 0 = 0
  | otherwise = last $ last dp
  where
    n = length weights
    dp = [[maxValue i w | w <- [0..capacity]] | i <- [0..n]]
    
    maxValue 0 _ = 0
    maxValue i w
      | weights !! (i-1) > w = dp !! (i-1) !! w
      | otherwise = max (dp !! (i-1) !! w) 
                       (dp !! (i-1) !! (w - weights !! (i-1)) + values !! (i-1))