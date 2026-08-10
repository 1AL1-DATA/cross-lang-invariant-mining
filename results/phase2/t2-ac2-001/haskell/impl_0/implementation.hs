import qualified Data.Map as Map
import Data.Map (Map)
import Data.Set (Set)
import qualified Data.Set as Set

bfs :: Map Int [Int] -> Int -> [Int]
bfs graph start = go [start] Set.empty []
  where
    go [] _ result = reverse result
    go (x:xs) visited result
      | Set.member x visited = go xs visited result
      | otherwise =
          let neighbors = Map.findWithDefault [] x graph
              newVisited = Set.insert x visited
          in go (xs ++ neighbors) newVisited (x : result)