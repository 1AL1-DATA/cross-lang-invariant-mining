let rec split lst =
  match lst with
  | [] -> ([], [])
  | [x] -> ([x], [])
  | x :: y :: rest ->
    let left, right = split rest in
    (x :: left, y :: right)

let rec merge lst1 lst2 =
  match lst1, lst2 with
  | [], lst | lst, [] -> lst
  | h1 :: t1, h2 :: t2 ->
    if h1 <= h2 then h1 :: merge t1 lst2
    else h2 :: merge lst1 t2

let rec merge_sort lst =
  match lst with
  | [] | [_] -> lst
  | _ ->
    let left, right = split lst in
    merge (merge_sort left) (merge_sort right)