type 'a node =
  | Empty
  | Node of 'a * int * 'a node * 'a node

let height = function
  | Empty -> 0
  | Node (_, h, _, _) -> h

let make_node key left right =
  let h = 1 + max (height left) (height right) in
  Node (key, h, left, right)

let left_child = function
  | Empty -> Empty
  | Node (_, _, l, _) -> l

let right_child = function
  | Empty -> Empty
  | Node (_, _, _, r) -> r

let balance_factor node =
  (height (left_child node)) - (height (right_child node))

let rotate_right = function
  | Node (key, _, Node (left_key, _, left_left, left_right), right) ->
      make_node left_key left_left (make_node key left_right right)
  | node -> node

let rotate_left = function
  | Node (key, _, left, Node (right_key, _, right_left, right_right)) ->
      make_node right_key (make_node key left right_left) right_right
  | node -> node

let rebalance = function
  | Empty -> Empty
  | Node (key, _, left, right) as node ->
      if balance_factor node > 1 then
        let left_child = left_child node in
        if balance_factor left_child < 0 then
          let new_left = rotate_left left_child in
          make_node key new_left right
        else
          rotate_right node
      else if balance_factor node < -1 then
        let right_child = right_child node in
        if balance_factor right_child > 0 then
          let new_right = rotate_right right_child in
          make_node key left new_right
        else
          rotate_left node
      else
        node

let heights = function
  | Empty -> []
  | Node (key, _, left, right) ->
      let left_heights = heights left in
      let right_heights = heights right in
      left_heights @ [height (Node (key, 0, left, right))] @ right_heights

let rec insert key = function
  | Empty -> make_node key Empty Empty
  | Node (k, _, left, right) ->
      if key < k then
        let new_left = insert key left in
        rebalance (make_node k new_left right)
      else if key > k then
        let new_right = insert key right in
        rebalance (make_node k left new_right)
      else
        Node (k, height (Node (k, 0, left, right)), left, right)

let avl_insert keys =
  let root = List.fold_left (fun acc key -> insert key acc) Empty keys in
  (root, heights root)