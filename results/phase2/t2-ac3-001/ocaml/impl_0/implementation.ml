let rec merge lst1 lst2 =
  match lst1, lst2 with
  | [], lst -> lst
  | lst, [] -> lst
  | x :: xs, y :: ys ->
    if x <= y then x :: merge xs lst2
    else y :: merge lst1 ys

let rec split lst =
  match lst with
  | [] -> [], []
  | [x] -> [x], []
  | x :: y :: rest ->
    let left, right = split rest in
    x :: left, y :: right

let rec merge_sort lst =
  match lst with
  | [] -> []
  | [_] -> lst
  | _ ->
    let left, right = split lst in
    merge (merge_sort left) (merge_sort right)