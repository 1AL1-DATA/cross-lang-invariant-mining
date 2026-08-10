exception Parse_error of string

let rec tokenize s i len tokens =
  if i >= len then List.rev tokens
  else
    let c = s.[i] in
    if c = ' ' then tokenize s (i + 1) len tokens
    else if c = '+' then tokenize s (i + 1) len ((`Plus, i) :: tokens)
    else if c = '-' then tokenize s (i + 1) len ((`Minus, i) :: tokens)
    else if c = '*' then tokenize s (i + 1)