let top_k_elements lst k =
  let sorted = List.sort (fun a b -> compare b a) lst in
  let rec take n = function
    | [] -> []
    | x :: _ when n = 1 -> [x]
    | x :: xs -> x :: take (n - 1) xs
  in
  take k sorted