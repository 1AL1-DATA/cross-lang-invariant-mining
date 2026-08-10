let word_count lines =
  let split_words s =
    let rec aux acc start =
      if start >= String.length s then List.rev acc
      else if s.[start] = ' ' then aux acc (start + 1)
      else
        let rec find_end i =
          if i >= String.length s || s.[i] = ' ' then i
          else find_end (i + 1)
        in
        let word_len = find_end start - start in
        let word = String.sub s start word_len in
        aux (word :: acc) (find_end start)
    in
    List.rev (aux [] 0)
  in
  let map_phase line =
    let words = split_words line in
    List.map (fun w -> (String.lowercase_ascii w, 1)) words
  in
  let mapped = List.concat (List.map map_phase lines) in
  let rec reduce counts = function
    | [] -> counts
    | (word, count) :: rest ->
      let new_counts =
        match List.assoc_opt word counts with
        | Some n -> (word, n + count) :: List.remove_assoc word counts
        | None -> (word, count) :: counts
      in
      reduce new_counts rest
  in
  reduce [] mapped