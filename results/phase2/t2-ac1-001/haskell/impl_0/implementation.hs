import qualified Data.Map as Map

countCharacterFrequency :: String -> Map.Map Char Int
countCharacterFrequency s = Map.fromListWith (+) [(c, 1) | c <- s]