import Data.Map (Map)
import qualified Data.Map as Map
import Data.Set (Set)
import qualified Data.Set as Set

dfsIterative :: Map Int [Int] -> Int -> [Int]
dfsIterative graph start
  | Map.member start graph = reverse $ go [start] []
  | otherwise = [start]
  where
    go [] visited = visited
    go (x:xs) visited
      | x `Set.member` visited = go xs visited
      | otherwise = go (newNodes ++ xs) (x : visited)
      where
        newNodes = Map.findWithDefault [] x graph