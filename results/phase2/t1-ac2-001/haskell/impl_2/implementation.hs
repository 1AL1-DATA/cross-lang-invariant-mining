binarySearch :: [Int] -> Int -> Int
binarySearch [] _ = -1
binarySearch arr target = go 0 (length arr - 1)
  where
    go low high
      | low > high = -1
      | arr !! mid == target = mid
      | arr !! mid > target = go low (mid - 1)
      | otherwise = go (mid + 1) high
      where
        mid = low + (high - low) `div` 2