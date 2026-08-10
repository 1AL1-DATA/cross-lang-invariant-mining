type 'a tree =
  | Empty
  | Node of 'a tree * 'a * 'a tree

let level_order root =
  let rec aux current_level acc =
    match current_level with
    | [] -> List.rev acc
    | _ ->
      let values, next_level =
        List.fold_right
          (fun node (vals, next) ->
            match node with
            | Empty -> (vals, next)
            | Node (l, v, r) -> (v :: vals, next @ [l; r]))
          current_level
          ([], [])
      in
      aux next_level (values :: acc)
  in
  match root with
  | Empty -> []
  | _ -> aux [root] []