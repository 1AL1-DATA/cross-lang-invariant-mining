let knapsack weights values capacity =
  let n = List.length weights in
  if n = 0 || capacity < 0 then 0
  else
    let weights_arr = Array.of_list weights in
    let values_arr = Array.of_list values in
    let dp = Array.make_matrix (n + 1) (capacity + 1) 0 in
    for i = 1 to n do
      for w = 0 to capacity do
        let without_item = dp.(i-1).(w) in
        let with_item =
          if weights_arr.(i-1) <= w then
            dp.(i-1).(w - weights_arr.(i-1)) + values_arr.(i-1)
          else
            min_int
        in
        dp.(i).(w) <- max without_item with_item
      done
    done;
    dp.(n).(capacity)