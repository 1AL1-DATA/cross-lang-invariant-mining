solve :: [Int] -> Int
solve lst = sum (map (^2) (filter (>0) lst))