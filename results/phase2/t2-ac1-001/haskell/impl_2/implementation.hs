module CharFreq (countCharacterFrequency) where

import qualified Data.Map as Map

countCharacterFrequency :: String -> Map.Map Char Int
countCharacterFrequency = foldr (\c -> Map.insertWith (+) c 1) Map.empty