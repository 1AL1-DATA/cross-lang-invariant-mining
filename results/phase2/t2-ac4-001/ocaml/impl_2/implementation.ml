module StringMap = Map.Make(String)

let group_by_key pairs =
  let add_to_map map (key, value) =
    let current = try StringMap.find key map with Not_found -> [] in
    StringMap.add key (value :: current) map
  in
  let result = List.fold_left add_to_map StringMap.empty pairs in
  StringMap.map List.rev result