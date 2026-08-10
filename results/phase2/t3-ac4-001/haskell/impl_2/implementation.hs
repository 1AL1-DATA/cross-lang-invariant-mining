module WordCount (word_counts) where

import qualified Data.Map as Map
import Data.Char (toLower)

word_counts :: [String] -> Map.Map String Int
word_counts = Map.fromListWith (+) . map (\w -> (map toLower w, 1)) . concatMap words