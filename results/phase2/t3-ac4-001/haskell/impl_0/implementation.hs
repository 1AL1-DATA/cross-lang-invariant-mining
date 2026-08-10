import Data.Map (Map)
import qualified Data.Map as Map
import Data.Char (toLower)

-- Map phase: each word becomes a (word, 1) pair (lowercased)
mapPhase :: String -> [(String, Int)]
mapPhase line = [(map toLower w, 1) | w <- words line]

-- Reduce phase: combine (word, count) pairs by summing counts per word
reducePhase :: [(String, Int)] -> Map String Int
reducePhase pairs = foldr (\(w, c) acc -> Map.insertWith (+) w c acc) Map.empty pairs

-- Main word count using map-reduce pattern
wordCount :: [String] -> Map String Int
wordCount lines = reducePhase (concatMap mapPhase lines)