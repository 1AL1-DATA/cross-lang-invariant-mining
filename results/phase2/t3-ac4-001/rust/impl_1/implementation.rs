use std::collections::HashMap;

pub fn word_count(lines: Vec<&str>) -> HashMap<String, usize> {
    let mut counts = HashMap::new();
    
    for line in lines {
        for word in line.split_whitespace() {
            let lower_word = word.to_lowercase();
            *counts.entry(lower_word).or_insert(0) += 1;
        }
    }
    
    counts
}