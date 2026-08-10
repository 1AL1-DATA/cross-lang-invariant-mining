type 'a node = 
  | Empty
  | Node of 'a * 'a node * 'a node * int

let height tree =
  match tree with
  | Empty -> 0
  | Node (_, _, _, h) -> h

let make_node key left right =
  let h = 1 + max (height left) (height right) in
  Node (key, left, right, h)

let rotate_right tree =
  match tree with
  | Node (k, Node (lk, ll, lr, _), r, _) ->
      make_node lk ll (make_node k lr r)
  | _ -> tree

let rotate_left tree =
  match tree with
  | Node (k, l, Node (rk, rl, rr, _), _) ->
      make_node rk (make_node k l rl) rr
  | _ -> tree

let balance_factor tree =
  match tree with
  | Empty -> 0
  | Node (_, l, r, _) -> height l - height r

let rebalance tree =
  let bal = balance_factor tree in
  match tree with
  | Node (k, l, r, _) when bal > 1 ->
      if balance_factor l >= 0 then
        rotate_right tree
      else
        rotate_right (make_node k (rotate_left l) r)
  | Node (k, l, r, _) when bal < -1 ->
      if balance_factor r <= 0 then