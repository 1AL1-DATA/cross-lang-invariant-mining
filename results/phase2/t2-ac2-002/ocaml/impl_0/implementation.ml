module IntMap = Map.Make(Int)
module IntSet = Set.Make(Int)

let dfs_iterative graph start =
  let visited = ref IntSet.empty in
  let stack = ref [start] in
  let result = ref [] in
  
  while !stack <> [] do
    match !stack with
    | [] -> ()
    | node :: rest ->
      stack := rest;
      if not (IntSet.mem node !visited) then begin
        visited := IntSet.add node !visited;
        result := node :: !result;
        (* Push neighbors in reverse order for correct DFS order *)
        (match IntMap.find_opt node graph with
         | Some neighbors ->
           List.iter (fun n ->
             if not (IntSet.mem n !visited) then
               stack := n :: !stack
           ) (List.rev neighbors)
         | None -> ())
      end
  done;
  
  List.rev !result