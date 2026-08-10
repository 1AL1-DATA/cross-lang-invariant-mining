let is_anagram s1 s2 =
  let len1 = String.length s1 in
  let len2 = String.length s2 in
  if len1 <> len2 then false
  else
    let counts = Array.make 256 0 in
    let update_counts s increment =
      for i = 0 to String.length s - 1 do
        let idx = Char.code s.[i] in
        counts.(idx) <- counts.(idx) + increment
      done
    in
    update_counts s1 1;
    update_counts s2 (-1);
    Array.for_all ((=) 0) counts