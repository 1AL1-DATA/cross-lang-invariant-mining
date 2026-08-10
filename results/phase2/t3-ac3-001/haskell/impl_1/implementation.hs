knapsack :: [Int] -> [Int] -> Int -> Int
knapsack weights values capacity
  | null weights || null values = 0
  | capacity < 0 = 0
  | otherwise = dp !! n !! capacity
  where
    n = length weights
    dp = [[maxValue i w | w <- [0..capacity]] | i <- [0..n]]
    
    maxValue :: Int -> Int -> Int
    maxValue 0 _ = 0
    maxValue i w
      | weights !! (i - 1) > w = dp !! (i - 1) !! w
      | otherwise = max 
          (dp !! (i - 1) !! w)
          (values !! (i - 1) + dp !! (i - 1) !! (w - weights !! (i - 1)))