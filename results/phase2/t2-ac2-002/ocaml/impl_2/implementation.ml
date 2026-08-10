let dfs_iterative (graph : (int, int list) Hashtbl.t) (start : int) : int list =
  let visited = Hashtbl.create 64 in
  let stack = Stack.create () in
  let result = ref [] in
  Stack.push start stack;
  while not (Stack.is_empty stack) do
    let node = Stack.pop stack in
    if not (Hashtbl.mem visited node) then begin
      Hashtbl.add visited node ();
      result := node :: !result;
      match Hashtbl.find_opt graph node with
      | Some neighbors -> List.iter (fun n -> Stack.push n stack) neighbors
      | None -> ()
    end
  done;
  List.rev !result