let knapsack weights values capacity =
  let n = List.length weights in
  if n = 0 || capacity < 0 then 0
  else
    let weight_arr = Array.of_list weights in
    let value_arr = Array.of_list values in
    let dp = Array.make_matrix (n + 1) (capacity + 1) 0 in
    for i = 1 to n do
      let w = weight_arr.(i - 1) in
      let v = value_arr.(i - 1) in
      for cap = 0 to capacity do
        dp.(i).(cap) <- dp.(i - 1).(cap);
        if w <= cap then
          let value_with_item = dp.(i - 1).(cap - w) + v in
          if value_with_item > dp.(i).(cap) then
            dp.(i).(cap) <- value_with_item
      done
    done;
    dp.(n).(capacity)