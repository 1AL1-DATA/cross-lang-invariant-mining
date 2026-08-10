let longest_common_subsequence s1 s2 =
  let m = String.length s1 in
  let n = String.length s2 in
  if m = 0 || n = 0 then 0
  else
    let dp = Array.make_matrix (m + 1) (n + 1) 0 in
    for i = 1 to m do
      for j = 1 to n do
        if s1.[i - 1] = s2.[j - 1] then
          dp.(i).(j) <- dp.(i - 1).(j - 1) + 1
        else
          dp.(i).(j) <- max dp.(i - 1).(j) dp.(i).(j - 1)
      done
    done;
    dp.(m).(n)