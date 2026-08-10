type value =
  | Int of int
  | Char of char
  | Float of float
  | List of value list

let rec flatten v =
  match v with
  | Int n -> [Int n]
  | Char c -> [Char c]
  | Float f -> [Float f]
  | List lst -> List.concat (List.map flatten lst)