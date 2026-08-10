let string_reverse s =
  let len = String.length s in
  let rec get_codepoints i acc =
    if i >= len then List.rev acc
    else
      let b = Char.code s.[i] in
      let num_bytes, initial_bits =
        if b land 0x80 = 0 then (1, b)
        else if b land 0xE0 = 0xC0 then (2, b land 0x1F)
        else if b land 0xF0 = 0xE0 then (3, b land 0x0F)
        else (4, b land 0x07