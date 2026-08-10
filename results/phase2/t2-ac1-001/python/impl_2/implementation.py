from collections import Counter

def count_character_frequency(s: str) -> dict[str, int]:
    return dict(Counter(s)) if s else {}