binarySearch :: [Int] -> Int -> Int
binarySearch [] _ = -1
binarySearch arr target = go 0 (length arr - 1)
  where
    go low high
      | low > high = -1
      | arr !! mid == target = mid
      | arr !! mid < target = go (mid + 1) high
      | otherwise = go low (mid - 1)
      where
        mid = (low + high) `div` 2