let knapsack weights values capacity =
  let n = List.length weights in
  if n = 0 || capacity <= 0 then 0
  else
    let weights_arr = Array.of_list weights in
    let values_arr = Array.of_list values in
    let dp = Array.make_matrix (n + 1) (capacity + 1) 0 in
    for i = 1 to n do
      let w = weights_arr.(i - 1) in
      let v = values_arr.(i - 1) in
      for cap = 0 to capacity do
        if w <= cap then
          dp.(i).(cap) <- max dp.(i - 1).(cap) (dp.(i - 1).(cap - w) + v)
        else
          dp.(i).(cap) <- dp.(i - 1).(cap)
      done
    done;
    dp.(n).(capacity)