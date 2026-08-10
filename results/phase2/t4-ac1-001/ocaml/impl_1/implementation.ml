let is_anagram s1 s2 =
  let len1 = String.length s1 in
  let len2 = String.length s2 in
  if len1 <> len2 then false
  else
    let count_chars str =
      let counts = Array.make 256 0 in
      for i = 0 to String.length str - 1 do
        let idx = Char.code str.[i] in
        counts.(idx) <- counts.(idx) + 1
      done;
      counts
    in
    count_chars s1 = count_chars s2