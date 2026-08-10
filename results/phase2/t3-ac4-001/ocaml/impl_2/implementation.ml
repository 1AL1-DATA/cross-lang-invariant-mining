let word_count lines =
  let module M = Map.Make(String) in
  
  (* Map phase: create intermediate map for each line *)
  let map_phase line =
    let words = String.split_on_char ' ' line in
    List.fold_left (fun acc w ->
      let low = String.lowercase_ascii w in
      let cnt = try M.find low acc with Not_found -> 0 in
      M.add low (cnt + 1) acc
    ) M.empty words
  in
  
  (* Create list of intermediate maps, one per line *)
  let per_line_maps = List.map map_phase lines in
  
  (* Reduce phase: merge all intermediate maps into one *)
  let result = List.fold_left (fun acc intermediate_map ->
    let merge_fn word count acc_map =
      let total = try M.find word acc_map with Not_found -> 0 in
      M.add word (total + count) acc_map
    in
    M.fold merge_fn intermediate_map acc
  ) M.empty per_line_maps
  in
  
  (* Convert to association list for dict-like output *)
  M.bindings result