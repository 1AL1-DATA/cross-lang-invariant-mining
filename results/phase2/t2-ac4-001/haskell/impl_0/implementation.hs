module GroupByKey where

import Data.Map (Map)
import qualified Data.Map as Map

groupByKey :: [(String, Int)] -> Map String [Int]
groupByKey = foldr (\(k, v) -> Map.insertWith (++) k [v]) Map.empty