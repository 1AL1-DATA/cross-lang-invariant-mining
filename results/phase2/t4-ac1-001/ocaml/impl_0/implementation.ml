let is_anagram s1 s2 =
  let sort_string s =
    s
    |> String.to_seq
    |> List.of_seq
    |> List.sort Char.compare
    |> List.to_seq
    |> String.of_seq
  in
  sort_string s1 = sort_string s2