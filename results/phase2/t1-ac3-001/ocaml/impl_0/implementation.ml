let factorial (n : int) : int =
  if n < 0 then invalid_arg "Factorial: n must be non-negative"
  else if n > 20 then invalid_arg "Factorial: n must be at most 20"
  else
    let rec aux acc i =
      if i > n then acc
      else aux (acc * i) (i + 1)
    in
    aux 1 1