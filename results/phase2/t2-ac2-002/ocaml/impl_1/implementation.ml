let dfs_iterative graph start =
  let visited = Hashtbl.create 16 in
  let stack = Stack.create () in
  let visited_order = ref [] in
  
  Hashtbl.add visited start true;
  Stack.push start stack;
  
  while not (Stack.is_empty stack) do
    let node = Stack.pop stack in
    visited_order := node :: !visited_order;
    
    match List.assoc_opt node graph with
    | Some neighbors ->
      List.iter (fun neighbor ->
        if not (Hashtbl.mem visited neighbor) then begin
          Hashtbl.add visited neighbor true;
          Stack.push neighbor stack
        end
      ) (List.rev neighbors)
    | None -> ()
  done;
  
  List.rev !visited_order