let binary_search arr target =
  let arr = Array.of_list arr in
  let len = Array.length arr in
  if len = 0 then -1
  else
    let rec search lo hi =
      if lo > hi then -1
      else
        let mid = (lo + hi) / 2 in
        let mid_val = arr.(mid) in
        if mid_val = target then mid
        else if mid_val > target then search lo (mid - 1)
        else search (mid + 1) hi
    in
    search 0 (len - 1)