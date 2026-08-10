let binary_search arr target =
  let rec search lo hi =
    if lo > hi then -1
    else
      let mid = lo + (hi - lo) / 2 in
      let mid_val = List.nth arr mid in
      if mid_val = target then mid
      else if mid_val > target then search lo (mid - 1)
      else search (mid + 1) hi
  in
  let len = List.length arr in
  if len = 0 then -1 else search 0 (len - 1)