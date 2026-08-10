let utf8_codepoint_length s i =
  let byte = int_of_char s.[i] in
  if byte < 0xc0 then 1
  else if byte < 0xe0 then 2
  else if byte < 0xf0 then 3
  else 4

let rec extract_codepoints s i len acc =
  if i >= len then List.rev acc
  else
    let cp_len = utf8_codepoint_length s i in
    let cp = String.sub s i cp_len in
    extract_codepoints s (i + cp_len) len (cp :: acc)

let reverse_string s =
  let codepoints = extract_codepoints s 0 (String.length s) [] in
  String.concat "" codepoints