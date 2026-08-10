let utf8_codepoint_length s i =
  let c = int_of_char s.[i] in
  if c < 0x80 then 1
  else if c land 0xE0 = 0xC0 then 2
  else if c land 0xF0 = 0xE0 then 3
  else if c land 0xF8 = 0xF0 then 4
  else 1

let rev_string s =
  let len = String.length s in
  if len = 0 then ""
  else
    let rec get_codepoints acc i =
      if i >= len then acc
      else
        let cp_len = utf8_codepoint_length s i in
        let codepoint = String.sub s i cp_len in
        get_codepoints (codepoint :: acc) (i + cp_len)
    in
    let codepoints = get_codepoints [] 0 in
    String.concat "" codepoints