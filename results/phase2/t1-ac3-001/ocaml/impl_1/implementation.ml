let factorial_iterative n =
  if n < 0 || n > 20 then
    invalid_arg "n must be between 0 and 20"
  else
    let rec loop acc i =
      if i > n then
        acc
      else
        loop (acc * i) (i + 1)
    in
    loop 1 1