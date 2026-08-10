type 'a tree =
  | Empty
  | Node of 'a * 'a tree * 'a tree

let level_order root =
  let rec collect queue acc =
    match queue with
    | [] -> List.rev acc
    | _ ->
      let values, children =
        List.fold_left
          (fun (vals, kids) node ->
            match node with
            | Empty -> (vals, kids)
            | Node (v, l, r) -> (v :: vals, kids @ [l; r]))
          ([], []) queue
      in
      collect children ((List.rev values) :: acc)
  in
  match root with
  | Empty -> []
  | _ -> collect [root] []