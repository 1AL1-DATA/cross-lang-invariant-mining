binarySearch :: [Int] -> Int -> Int
binarySearch [] _ = -1
binarySearch arr target = search 0 (length arr - 1)
  where
    search low high
      | low > high = -1
      | target == arr !! mid = mid
      | target < arr !! mid = search low (mid - 1)
      | otherwise = search (mid + 1) high
      where
        mid = (low + high) `div` 2