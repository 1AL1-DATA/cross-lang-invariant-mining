data NestedList a = Element a | Sublist [NestedList a]
  deriving (Show, Eq)

flatten :: NestedList a -> [a]
flatten (Element x) = [x]
flatten (Sublist xs) = concatMap flatten xs