function wordCount(lines: string[]): Record<string, number> {
    if (lines.length === 0) {
        return {};
    }

    // Map phase: emit (word, 1) for each word in each line
    const mapped: [string, number][] = lines.flatMap(line =>
        line.split(' ').filter(word => word.length > 0).map(word => [word.toLowerCase(), 1] as [string, number])
    );

    // Reduce phase: aggregate counts by word
    return mapped.reduce<Record<string, number>>((counts, [word, count]) => {
        counts[word] = (counts[word] || 0) + count;
        return counts;
    }, {});
}