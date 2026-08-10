module CountCharacterFrequency where

import Data.Map (Map, fromListWith)

countCharacterFrequency :: String -> Map Char Int
countCharacterFrequency = fromListWith (+) . map (\c -> (c, 1))