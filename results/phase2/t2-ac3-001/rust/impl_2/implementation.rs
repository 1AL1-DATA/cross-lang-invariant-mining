pub fn merge_sort(lst: Vec<i32>) -> Vec<i32> {
    if lst.len() <= 1 {
        return lst;
    }
    let mid = lst.len() / 2;
    let left = merge_sort(lst[..mid].to_vec());
    let right = merge_sort(lst[mid..].to_vec());
    merge(&left, &right)
}

fn merge(left: &[i32], right: &[i32]) -> Vec<i32> {
    let mut result = Vec::with_capacity(left.len() + right.len());
    let mut i = 0;
    let mut j = 0;
    while i < left.len() && j < right.len() {
        if left[i] <= right[j] {
            result.push(left[i]);
            i += 1;
        } else {
            result.push(right[j]);
            j += 1;
        }
    }
    if i < left.len() {
        result.extend_from_slice(&left[i..]);
    }
    if j < right.len() {
        result.extend_from_slice(&right[j..]);
    }
    result
}