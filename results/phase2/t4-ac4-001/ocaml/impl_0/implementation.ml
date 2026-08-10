let filter_map_reduce lst =
  lst
  |> List.filter (fun x -> x > 0)
  |> List.map (fun x -> x * x)
  |> List.fold_left (+) 0