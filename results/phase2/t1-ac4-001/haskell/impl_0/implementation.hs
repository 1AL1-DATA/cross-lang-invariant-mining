-- Using a recursive type to handle arbitrary nesting
data NestedList a = Elem a | List [NestedList a]

flatten :: NestedList a -> [a]
flatten (Elem x) = [x]
flatten (List xs) = concatMap flatten xs

-- Convert regular lists to NestedList, flatten, and return result
-- This allows working with [[Int]] or deeper nesting
flattenDeep :: [[a]] -> [a]
flattenDeep = flatten . List . map List