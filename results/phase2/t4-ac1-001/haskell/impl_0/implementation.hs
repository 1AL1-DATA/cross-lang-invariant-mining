isAnagram :: String -> String -> Bool
isAnagram s1 s2 = sort s1 == sort s2
  where sort = Data.List.sort