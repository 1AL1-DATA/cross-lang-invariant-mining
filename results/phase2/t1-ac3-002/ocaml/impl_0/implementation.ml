let fibonacci n =
  match n with
  | 0 -> 0
  | 1 -> 1
  | _ ->
    let rec loop a b count =
      if count = n then b
      else loop b (a + b) (count + 1)
    in
    loop 1 1 2