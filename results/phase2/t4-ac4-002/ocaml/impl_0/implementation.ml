let eval expr =
  let len = String.length expr in
  let i = ref 0 in

  let peek () = if !i < len then expr.[!i] else '\000' in
  let advance () = let c = peek () in incr i; c in

  let rec parse_expression () =
    let result = ref (parse_term ()) in
    while peek () = '+' || peek () = '-' do
      let op = advance () in
      let right = parse_term () in
      result := if op = '+' then !result + right else !result - right
    done;
    !result

  and parse_term () =
    let result = ref (parse_factor ()) in
    while peek () = '*' || peek () = '/' do
      let op = advance () in
      let right = parse_factor () in
      result := if op = '*' then !result * right else !result / right
    done;
    !result

  and parse_factor () =
    let c = peek () in
    if c = '(' then (
      advance ();
      let result = parse_expression () in
      ignore (advance ());
      result
    ) else (
      let num = ref 0 in
      while match peek () with '0'..'9' -> true | _ -> false do
        num := !num * 10 + (Char.code (advance ()) - Char.code '0')
      done;
      !num
    )
  in
  parse_expression ()