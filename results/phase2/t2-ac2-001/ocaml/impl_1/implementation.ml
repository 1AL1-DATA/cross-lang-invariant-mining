let bfs graph start =
  let visited = ref [] in
  let queue = Queue.create () in
  let visited_set = ref [] in
  
  Queue.add start queue;
  visited_set := start :: !visited_set;
  
  while not (Queue.is_empty queue) do
    let node = Queue.take queue in
    visited := node :: !visited;
    
    let neighbors = match List.assoc_opt node graph with
      | Some ns -> ns
      | None -> []
    in
    
    List.iter (fun neighbor ->
      if not (List.mem neighbor !visited_set) then begin
        Queue.add neighbor queue;
        visited_set := neighbor :: !visited_set
      end
    ) neighbors
  done;
  
  List.rev !visited