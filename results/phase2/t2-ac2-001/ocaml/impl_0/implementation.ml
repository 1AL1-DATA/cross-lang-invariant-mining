let bfs graph start =
  let rec aux queue visited acc =
    match queue with
    | [] -> List.rev acc
    | node :: rest ->
      if List.mem node visited then
        aux rest visited acc
      else
        let neighbors = try List.assoc node graph with Not_found -> [] in
        aux (List.rev_append rest neighbors) (node :: visited) (node :: acc)
  in
  aux [start] [] []