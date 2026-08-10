use std::collections::HashMap;

pub fn is_anagram(s1: &str, s2: &str) -> bool {
    if s1.len() != s2.len() {
        return false;
    }

    let mut char_counts: HashMap<char, i32> = HashMap::new();

    for c in s1.chars() {
        *char_counts.entry(c).or_insert(0) += 1;
    }

    for c in s2.chars() {
        match char_counts.get_mut(&c) {
            Some(count) => *count -= 1,
            None => return false,
        }
    }

    char_counts.values().all(|&count| count == 0)
}