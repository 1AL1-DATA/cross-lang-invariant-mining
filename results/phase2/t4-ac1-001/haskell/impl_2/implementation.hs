import Data.List (sort)

isAnagram :: String -> String -> Bool
isAnagram s1 s2 = sort s1 == sort s2