module Factorial where

factorial :: Int -> Integer
factorial n
  | n < 0  = error "Factorial: negative input"
  | n > 20 = error "Factorial: input too large"
  | n == 0 = 1
  | otherwise = product [1..n]