module StringMap = Map.Make(String)

let group_by_key pairs =
  List.fold_left (fun acc (key, value) ->
    match StringMap.find_opt key acc with
    | None -> StringMap.add key [value] acc
    | Some values -> StringMap.add key (value :: values) acc
  ) StringMap.empty pairs