module CharMap = Map.Make(Char)

let count_character_frequency s =
  String.fold_left (fun counts c ->
    CharMap.update c (function
      | None -> Some 1
      | Some n -> Some (n + 1)
    ) counts
  ) CharMap.empty s