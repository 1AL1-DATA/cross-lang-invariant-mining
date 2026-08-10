let fibonacci n =
  if n = 0 then 0
  else if n = 1 then 1
  else
    let rec loop a b count =
      if count = n then a + b
      else loop b (a + b) (count + 1)
    in
    loop 0 1 1