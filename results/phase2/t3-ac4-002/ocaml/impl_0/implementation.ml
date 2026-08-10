let top_k_elements (lst : int list) (k : int) : int list =
  let sorted = List.sort (fun a b -> b - a) lst in
  let rec take n acc = function
    | [] -> List.rev acc
    | x :: xs -> if n = 0 then List.rev acc else take (n - 1) (x :: acc) xs
  in
  take k [] sorted