type 'a node = {
  value : 'a;
  left : 'a node option;
  right : 'a node option;
}

let level_order root =
  let rec process_level nodes result =
    match nodes with
    | [] -> List.rev result
    | _ ->
      let values = List.map (fun n -> n.value) nodes in
      let next_level =
        List.concat_map (fun n ->
          match n.left, n.right with
          | Some l, Some r -> [l; r]
          | Some l, None -> [l]
          | None, Some r -> [r]
          | None, None -> []
        ) nodes
      in
      process_level next_level (values :: result)
  in
  match root with
  | None -> []
  | Some node -> process_level [node] []