use std::collections::HashMap;

pub fn are_anagrams(s1: &str, s2: &str) -> bool {
    if s1.len() != s2.len() {
        return false;
    }

    let mut count = HashMap::new();

    for c in s1.chars() {
        *count.entry(c).or_insert(0) += 1;
    }

    for c in s2.chars() {
        match count.entry(c).or_insert(0) {
            count if *count == 0 => return false,
            count => *count -= 1,
        }
    }

    true
}