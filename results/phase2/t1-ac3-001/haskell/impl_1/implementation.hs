module Factorial (factorial) where

factorial :: Integer -> Integer
factorial n
  | n < 0     = error "factorial: negative argument"
  | n > 20    = error "factorial: argument exceeds 20"
  | otherwise = iter n 1
  where
    iter 0 acc = acc
    iter k acc = iter (k - 1) (acc * k)