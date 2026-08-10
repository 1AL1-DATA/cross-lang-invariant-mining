module StringMap = Map.Make(String)

let word_count lines =
  let add_word map word =
    let count =
      try StringMap.find word map
      with Not_found -> 0
    in
    StringMap.add word (count + 1) map
  in
  let map_line line =
    Str.split (Str.regexp "[ \t]+") line
    |> List.map String.lowercase_ascii
  in
  let map_all = List.concat_map map_line in
  let reduce = List.fold_left add_word StringMap.empty in
  reduce (map_all lines)