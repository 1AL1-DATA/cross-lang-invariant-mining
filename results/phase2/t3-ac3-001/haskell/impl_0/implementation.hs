module Knapsack where

knapsack :: [Int] -> [Int] -> Int -> Int
knapsack weights values capacity
  | capacity < 0 = 0
  | null weights || null values = 0
  | otherwise = last dp
  where
    dp = foldl updateDP (replicate (capacity + 1) 0) (zip weights values)
    
    updateDP :: [Int] -> (Int, Int) -> [Int]
    updateDP currentDP (w, v) = newDP
      where
        newDP = [ if i >= w 
                  then max (currentDP !! i) (currentDP !! (i - w) + v)
                  else currentDP !! i
                | i <- [0..capacity] ]