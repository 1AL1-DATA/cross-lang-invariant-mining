use std::collections::HashMap;

pub fn word_count(lines: Vec<&str>) -> HashMap<String, usize> {
    // Map phase: transform each line into (word, 1) pairs
    let mapped: Vec<(String, usize)> = lines
        .iter()
        .flat_map(|line| {
            line.split_whitespace()
                .map(|word| (word.to_lowercase(), 1))
                .collect::<Vec<_>>()
        })
        .collect();

    // Reduce phase: combine counts for the same word
    let mut word_counts: HashMap<String, usize> = HashMap::new();
    for (word, count) in mapped {
        *word_counts.entry(word).or_insert(0) += count;
    }

    word_counts
}