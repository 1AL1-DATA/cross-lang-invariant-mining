filterMapReduce :: [Int] -> Int
filterMapReduce = sum . map (^2) . filter (> 0)