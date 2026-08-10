import Data.Set (Set)
import qualified Data.Set as Set
import Data.Maybe (fromMaybe)

bfs :: [(Int, [Int])] -> Int -> [Int]
bfs graph start = bfs' [start] Set.empty
  where
    bfs' [] _ = []
    bfs' (x:xs) visited
      | x `Set.member` visited = bfs' xs visited
      | otherwise = x : bfs' (xs ++ neighbors) (Set.insert x visited)
      where
        neighbors = fromMaybe [] (lookup x graph)