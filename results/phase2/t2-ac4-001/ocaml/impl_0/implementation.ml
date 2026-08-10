let group_by_key pairs =
  let add_pair (key, value) acc =
    match acc with
    | [] -> [(key, [value])]
    | (k, vs) :: rest ->
      if k = key then (k, value :: vs) :: rest
      else (k, vs) :: add_pair (key, value) rest
  in
  List.fold_left (fun acc pair -> add_pair pair acc) [] pairs