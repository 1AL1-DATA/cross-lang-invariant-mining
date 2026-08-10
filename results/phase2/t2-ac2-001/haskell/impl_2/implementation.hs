module BFS (bfs) where

import qualified Data.Map as M
import qualified Data.Set as S

bfs :: M.Map Int [Int] -> Int -> [Int]
bfs graph start = go [start] (S.singleton start)
  where
    go [] _ = []
    go (x:xs) visited = x : go (xs ++ newNodes) (S.union visited (S.fromList newNodes))
      where
        neighbors = M.findWithDefault [] x graph
        newNodes  = filter (`S.notMember` visited) neighbors