function countCharacterFrequency(s: string): Record<string, number> {
    const counts: Record<string, number> = {};
    
    for (const char of s) {
        counts[char] = (counts[char] || 0) + 1;
    }
    
    return counts;
}