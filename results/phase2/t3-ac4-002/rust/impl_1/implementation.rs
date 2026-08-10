fn top_k_elements(mut lst: Vec<i32>, k: usize) -> Vec<i32> {
    if k >= lst.len() {
        lst.sort_by(|a, b| b.cmp(a));
        return lst;
    }
    
    lst.sort_unstable();
    lst.into_iter().rev().take(k).collect()
}