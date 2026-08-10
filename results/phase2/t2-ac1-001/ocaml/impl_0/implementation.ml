let count_character_frequency (s : string) : (char, int) Map.Make(Char).t =
  let module M = Map.Make(Char) in
  String.fold_left
    (fun acc c ->
       let new_count = match M.find_opt c acc with
         | None -> 1
         | Some n -> n + 1
       in
       M.add c new_count acc)
    M.empty
    s