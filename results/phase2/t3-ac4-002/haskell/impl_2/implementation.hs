import Data.List (sortBy)

topK :: Ord a => [a] -> Int -> [a]
topK lst k = take k $ sortBy (flip compare) lst