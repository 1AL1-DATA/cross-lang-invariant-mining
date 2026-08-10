def is_anagram(s1: str, s2: str) -> bool:
    """
    Return True if the two strings are anagrams of each other.
    Comparison is case-sensitive and includes all characters.
    Empty strings are considered anagrams.
    """
    if len(s1) != len(s2):
        return False
    from collections import Counter
    return Counter(s1) == Counter(s2)