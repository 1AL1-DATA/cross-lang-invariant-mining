import Data.Map (Map)
import qualified Data.Map as Map
import Data.Set (Set)
import qualified Data.Set as Set

type Graph = Map Int [Int]

dfsIterative :: Graph -> Int -> [Int]
dfsIterative graph start = go [start] [] Set.empty
  where
    go [] result _ = reverse result
    go (x:xs) result visited
      | Set.member x visited = go xs result visited
      | otherwise = go (neighbors ++ xs) (x:result) (Set.insert x visited)
      where
        neighbors = Map.findWithDefault [] x graph