let longest_common_subsequence s1 s2 =
  let n = String.length s1 in
  let m = String.length s2 in
  let dp = Array.make_matrix (n + 1) (m + 1) 0 in
  for i = 1 to n do
    for j = 1 to m do
      if s1.[i - 1] = s2.[j - 1] then
        dp.(i).(j) <- dp.(i - 1).(j - 1) + 1
      else
        dp.(i).(j) <- max dp.(i - 1).(j) dp.(i).(j - 1)
    done
  done;
  dp.(n).(m)