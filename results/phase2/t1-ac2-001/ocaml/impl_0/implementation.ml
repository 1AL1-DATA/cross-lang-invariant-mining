let binary_search arr target =
  let rec search low high =
    if low > high then -1
    else
      let mid = (low + high) / 2 in
      let mid_val = arr.(mid) in
      if mid_val = target then mid
      else if mid_val < target then search (mid + 1) high
      else search low (mid - 1)
  in
  search 0 (Array.length arr - 1)