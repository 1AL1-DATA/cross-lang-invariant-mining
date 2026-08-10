import Data.List (sort)

topKElements :: Ord a => [a] -> Int -> [a]
topKElements lst k = take k (reverse (sort lst))