from collections import Counter

def word_count(lines):
    """
    Count word frequencies using a map-then-reduce pattern.
    Case-insensitive.
    
    Args:
        lines (list[str]): list of input lines
        
    Returns:
        dict[str, int]: word → total count
    """
    if not lines:
        return {}
    
    # Map phase: split each line into words and convert to lowercase
    def map_phase(line):
        return [word.lower() for word in line.split()]
    
    # Apply map to all lines
    mapped_results = [map_phase(line) for line in lines]
    
    # Flatten mapped results
    all_words = []
    for words in mapped_results:
        all_words.extend(words)
    
    # Reduce phase: count word frequencies
    return dict(Counter(all_words))