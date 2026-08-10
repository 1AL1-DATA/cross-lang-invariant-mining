let compose_n_functions funcs x =
  List.fold_left (fun acc f -> f acc) x funcs