def count_character_frequency(s: str) -> dict[str, int]:
    counts = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    return counts