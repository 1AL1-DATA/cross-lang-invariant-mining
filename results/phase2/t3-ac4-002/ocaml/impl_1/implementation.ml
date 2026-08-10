let top_k_elements lst k =
  let sorted = List.sort (fun a b -> compare b a) lst in
  let rec take n = function
    | [] -> []
    | x :: xs -> if n > 0 then x :: take (n - 1) xs else []
  in
  take k sorted