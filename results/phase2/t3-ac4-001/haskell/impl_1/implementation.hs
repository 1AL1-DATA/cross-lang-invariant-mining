import Data.Map (Map)
import qualified Data.Map as Map
import Data.Char (toLower)

wordCount :: [String] -> Map String Int
wordCount lines = Map.fromListWith (+) $ mapReduceStep lines
  where
    mapStep :: String -> [(String, Int)]
    mapStep line = map (\word -> (map toLower word, 1)) (words line)
    
    mapReduceStep :: [String] -> [(String, Int)]
    mapReduceStep = concatMap mapStep
    
    reduceStep :: [(String, Int)] -> Map String Int
    reduceStep = Map.fromListWith (+)