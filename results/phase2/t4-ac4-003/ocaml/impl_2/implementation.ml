let compose_n_functions (funcs : (int -> int) list) (x : int) : int =
  List.fold_left (fun acc f -> f acc) x funcs