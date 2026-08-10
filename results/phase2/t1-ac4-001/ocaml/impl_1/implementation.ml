type 'a item =
  | Elem of 'a
  | List of 'a item list

let rec flatten (lst : 'a item list) : 'a list =
  match lst with
  | [] -> []
  | Elem x :: t -> x :: flatten t
  | List l :: t -> flatten l @ flatten t