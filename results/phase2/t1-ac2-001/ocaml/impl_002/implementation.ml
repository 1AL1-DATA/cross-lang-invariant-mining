let rec solution = function
  | Empty -> 0
  | Node (_, l, r) -> 1 + max (solution l) (solution r)
