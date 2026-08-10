type 'a avl_tree =
  | Empty
  | Node of {
      key: 'a;
      left: 'a avl_tree;
      right: 'a avl_tree;
      height: int
    }

let height tree =
  match tree with
  | Empty -> 0
  | Node { height; _ } -> height

let make_node key left right =
  let h = 1 + max (height left) (height right) in
  Node { key; left; right; height = h }

let balance_factor tree =
  match tree with
  | Empty -> 0
  | Node { left; right; _ } -> height left - height right

let rotate_right tree =
  match tree with
  | Node { key; left = Node { key = lk; left = ll; right = lr }; right; height = _ } ->
    let new_right = make_node key lr right in
    make_node lk ll new_right
  | _ -> tree

let rotate_left tree =
  match tree with
  | Node { key; left; right = Node { key = rk; left = rl; right = rr }; height = _ } ->
    let new_left = make_node key left rl in
    make_node rk new_left rr
  | _ -> tree

let balance tree =
  match tree with
  | Empty -> Empty
  | Node ({ key; left; right; height = _ } as node) ->
    let bf = balance_factor tree in
    if bf > 1 then
      if balance_factor left >= 0 then
        rotate_right tree
      else
        let new_left = rotate_left left in
        rotate_right (Node { node with left = new_left })
    else if bf < -1 then
      if balance_factor right <= 0 then
        rotate_left tree
      else
        let new_right = rotate_right right in
        rotate_left (Node { node with right = new_right })
    else
      tree

let rec insert key tree =
  match tree with
  | Empty -> make_node key Empty Empty
  | Node ({ key = k; left; right; height = _ } as node) ->
    if key = k then tree
    else if key < k then
      let new_left = insert key left in
      balance (Node { node with left = new_left })
    else
      let new_right = insert key right in
      balance (Node { node with right = new_right })

let rec in_order_heights tree =
  match tree with
  | Empty -> []
  | Node { key; left; right; height } ->
    (in_order_heights left) @ [height] @ (in_order_heights right)

let avl_insert keys =
  let rec aux acc = function
    | [] -> acc
    | k :: rest -> aux (insert k acc) rest
  in
  let root = aux Empty keys in
  (root, in_order_heights root)

let search key tree =
  let rec aux = function
    | Empty -> false
    | Node { key = k; left; right; height = _ } ->
      if key = k then true
      else if key < k then aux left
      else aux right
  in
  aux tree