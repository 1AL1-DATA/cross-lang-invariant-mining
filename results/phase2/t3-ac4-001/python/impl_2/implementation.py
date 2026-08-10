def word_count(lines):
    """
    Count word frequencies using a map-reduce pattern.
    
    Args:
        lines (list[str]): list of input lines
    
    Returns:
        dict[str, int]: word → total count (case-insensitive)
    """
    if not lines:
        return {}
    
    # Map phase: extract and lowercase all words from all lines
    # (split by whitespace)
    all_words = []
    for line in lines:
        words = line.split()
        all_words.extend(word.lower() for word in words)
    
    # Reduce phase: count word frequencies
    word_counts = {}
    for word in all_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    return word_counts