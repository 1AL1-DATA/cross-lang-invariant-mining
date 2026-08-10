import Data.Map (Map)
import qualified Data.Map as Map

groupByKey :: [(String, Int)] -> Map String [Int]
groupByKey pairs = foldr insertPair Map.empty pairs
  where
    insertPair (key, value) acc = Map.insertWith (++) key [value] acc