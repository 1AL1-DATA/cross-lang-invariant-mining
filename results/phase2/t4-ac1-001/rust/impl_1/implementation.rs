use std::collections::HashMap;

pub fn is_anagram(s1: &str, s2: &str) -> bool {
    if s1.len() != s2.len() {
        return false;
    }
    
    let mut count = HashMap::new();
    
    for c in s1.chars() {
        *count.entry(c).or_insert(0) += 1;
    }
    
    for c in s2.chars() {
        match count.get_mut(&c) {
            Some(v) => *v -= 1,
            None => return false,
        }
    }
    
    count.values().all(|&v| v == 0)
}