function wordCount(lines: string[]): Record<string, number> {
    const wordCounts: Record<string, number> = {};
    
    for (const line of lines) {
        const words = line.split(/\s+/);
        for (const word of words) {
            const normalizedWord = word.toLowerCase();
            wordCounts[normalizedWord] = (wordCounts[normalizedWord] || 0) + 1;
        }
    }
    
    return wordCounts;
}