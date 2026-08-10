let rec split lst =
  match lst with
  | [] -> ([], [])
  | [x] -> ([x], [])
  | x :: y :: rest ->
    let (first, second) = split rest in
    (x :: first, y :: second)

let rec merge lst1 lst2 =
  match (lst1, lst2) with
  | ([], []) -> []
  | ([], l) -> l
  | (l, []) -> l
  | (x :: rest1, y :: rest2) ->
    if x <= y then x :: merge rest1 (y :: rest2)
    else y :: merge (x :: rest1) rest2

let rec merge_sort lst =
  match lst with
  | [] -> []
  | [_] -> lst
  | _ ->
    let (first, second) = split lst in
    let sorted_first = merge_sort first in
    let sorted_second = merge_sort second in
    merge sorted_first sorted_second