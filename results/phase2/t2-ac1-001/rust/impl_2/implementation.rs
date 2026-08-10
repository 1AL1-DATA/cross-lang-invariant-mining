use std::collections::HashMap;

pub fn count_character_frequency(s: &str) -> HashMap<char, usize> {
    let mut counts = HashMap::new();
    for c in s.chars() {
        *counts.entry(c).or_insert(0) += 1;
    }
    counts
}