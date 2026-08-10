use std::collections::HashMap;

fn word_count(lines: Vec<String>) -> HashMap<String, i32> {
    // Map phase: convert each line into (word, 1) pairs
    let mapped: Vec<(String, i32)> = lines
        .iter()
        .flat_map(|line| {
            line.split_whitespace()
                .map(|word| (word.to_lowercase(), 1))
                .collect::<Vec<_>>()
        })
        .collect();

    // Reduce phase: combine counts for identical words
    let mut word_counts: HashMap<String, i32> = HashMap::new();
    for (word, count) in mapped {
        *word_counts.entry(word).or_insert(0) += count;
    }

    word_counts
}