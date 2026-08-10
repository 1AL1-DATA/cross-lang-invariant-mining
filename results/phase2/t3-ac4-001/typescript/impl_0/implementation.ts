function wordCount(lines: string[]): Record<string, number> {
    const wordCounts = lines
        .flatMap(line => line.split(/\s+/))
        .filter(word => word.length > 0)
        .map(word => word.toLowerCase())
        .reduce<Map<string, number>>((counts, word) => {
            counts.set(word, (counts.get(word) || 0) + 1);
            return counts;
        }, new Map());
    
    return Object.fromEntries(wordCounts);
}