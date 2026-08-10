import Data.Map (Map)
import qualified Data.Map as Map

groupByKey :: [(String, Int)] -> Map String [Int]
groupByKey = Map.fromListWith (++) . fmap (\(k, v) -> (k, [v]))