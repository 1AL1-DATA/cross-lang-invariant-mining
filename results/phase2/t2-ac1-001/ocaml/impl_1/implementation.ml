let count_character_frequency s =
  let module M = Map.Make(Char) in
  let counts = ref M.empty in
  String.iter (fun c ->
    let new_count =
      match M.find_opt c !counts with
      | None -> 1
      | Some n -> n + 1
    in
    counts := M.add c new_count !counts
  ) s;
  !counts