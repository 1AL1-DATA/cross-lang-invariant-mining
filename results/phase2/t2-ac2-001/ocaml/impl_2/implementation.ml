let bfs (graph : (int, int list) Hashtbl.t) (start : int) : int list =
  let visited = Hashtbl.create 64 in
  let queue = Queue.create () in
  let result = ref [] in
  
  Hashtbl.add visited start;
  Queue.add start queue;
  
  while not (Queue.is_empty queue) do
    let current = Queue.take queue in
    result := current :: !result;
    
    match Hashtbl.find_opt graph current with
    | Some neighbors ->
      List.iter (fun neighbor ->
        if not (Hashtbl.mem visited neighbor) then begin
          Hashtbl.add visited neighbor;
          Queue.add neighbor queue
        end
      ) neighbors
    | None -> ()
  done;
  
  List.rev !result