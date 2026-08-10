from collections import defaultdict

def word_count(lines):
    if not lines:
        return {}
    
    # Map phase: split each line into words (case-insensitive)
    def map_func(line):
        return line.lower().split()
    
    all_words = []
    for line in lines:
        all_words.extend(map_func(line))
    
    # Reduce phase: aggregate word counts
    word_counts = defaultdict(int)
    for word in all_words:
        word_counts[word] += 1
    
    return dict(word_counts)