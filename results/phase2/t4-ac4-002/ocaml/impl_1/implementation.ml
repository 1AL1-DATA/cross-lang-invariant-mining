type token =
  | Num of int
  | Plus
  | Minus
  | Times
  | Divide
  | Lparen
  | Rparen

let rec lex_expr (s : string) : token list =
  let rec lex i tokens =
    if i >= String.length s then List.rev tokens
    else
      let c = s.[i] in
      match c with
      | ' ' -> lex (i + 1) tokens
      | '+' -> lex (i + 1) (Plus :: tokens)
      | '-' -> lex (i + 1) (Minus :: tokens)
      | '*' -> lex (i + 1) (Times :: tokens)
      | '/' -> lex (i + 1) (Divide :: tokens)
      | '(' -> lex (i + 1) (Lparen :: tokens)
      | ')' -> lex (i + 1) (Rparen :: tokens)
      | _ ->
          if c >= '0' && c <= '9' then
            let rec read_number j num =
              if j >= String.length s || s.[j] < '0' || s.[j] > '9' then
                (num, j)
              else
                read_number (j + 1) (num * 10 + (Char.code s.[j] - Char.code '0'))
            in
            let (num, next_i) = read_number i 0 in
            lex next_i (Num num :: tokens)
          else
            failwith "Invalid character"
  in
  lex 0 []

let eval (s : string) : int =
  let tokens = lex_expr s in
  let rec parse_expr (toks : token list) pos =
    let (value, new_pos) = parse_term toks pos in
    let rec loop acc p =
      if p >= List.length toks then (acc, p)
      else
        match List.nth toks p with
        | Plus ->
            let (right_val, new_p) = parse_term toks (p + 1) in
            loop (acc + right_val) new_p
        | Minus ->
            let (right_val, new_p) = parse_term toks (p + 1) in
            loop (acc - right_val) new_p
        | _ -> (acc, p)
    in
    loop value new_pos
  
  and parse_term (toks : token list) pos =
    let (value, new_pos) = parse_factor toks pos in
    let rec loop acc p =
      if p >= List.length toks then (acc, p)
      else
        match List.nth toks p with
        | Times ->
            let (right_val, new_p) = parse_factor toks (p + 1) in
            loop (acc * right_val) new_p
        | Divide ->
            let (right_val, new_p) = parse_factor toks (p + 1) in
            loop (acc / right_val) new_p
        | _ -> (acc, p)
    in
    loop value new_pos
  
  and parse_factor (toks : token list) pos =
    if pos >= List.length toks then failwith "Unexpected end of expression"
    else
      match List.nth toks pos with
      | Num n -> (n, pos + 1)
      | Lparen ->
          let (value, new_pos) = parse_expr toks (pos + 1) in
          if new_pos >= List.length toks || List.nth toks new_pos != Rparen then
            failwith "Missing closing parenthesis"
          else
            (value, new_pos + 1)
      | _ -> failwith "Unexpected token"
  in
  let (result, _) = parse_expr tokens 0 in
  result

let evaluate_arithmetic_expression (expr : string) : int = eval expr