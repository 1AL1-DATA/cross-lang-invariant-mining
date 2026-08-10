type nested =
  | V of 'a
  | N of nested list

let rec flatten (lst : nested list) : 'a list =
  let unbox elem =
    match elem with
    | V x -> [x]
    | N l -> flatten l
  in
  List.concat (List.map unbox lst)

let flatten_list (lst : nested list) = flatten lst