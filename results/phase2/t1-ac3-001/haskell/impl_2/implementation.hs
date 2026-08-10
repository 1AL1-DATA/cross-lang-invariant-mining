factorial :: Int -> Integer
factorial n
  | n < 0   = error "factorial: negative argument"
  | n > 20  = error "factorial: argument exceeds 20"
  | otherwise = loop n 1
  where
    loop 0 acc = acc
    loop i acc = loop (i - 1) (acc * toInteger i)