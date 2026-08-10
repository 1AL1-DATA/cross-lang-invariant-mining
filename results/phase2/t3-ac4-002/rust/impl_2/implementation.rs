fn top_k_elements(lst: Vec<i32>, k: usize) -> Vec<i32> {
    let mut sorted = lst;
    sorted.sort_by(|a, b| b.cmp(a));
    sorted.into_iter().take(k).collect()
}