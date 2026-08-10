fn filter_map_reduce(lst: &[i32]) -> i32 {
    lst.iter()
        .filter(|&&x| x > 0)
        .map(|&x| x * x)
        .sum()
}