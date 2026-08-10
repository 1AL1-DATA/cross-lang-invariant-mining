import Data.Map.Strict (Map)
import qualified Data.Map.Strict as Map
import Data.Set (Set)
import qualified Data.Set as Set

dfsIterative :: Map Int [Int] -> Int -> [Int]
dfsIterative graph start = reverse (go [start] Set.empty [])
  where
    go [] _ result = result
    go (x:xs) visited result
      | Set.member x visited = go xs visited result
      | otherwise = go (neighbors ++ xs) (Set.insert x visited) (x:result)
      where
        neighbors = Map.findWithDefault [] x graph