function groupByKey(pairs: Array<[string, number]>): Record<string, number[]> {
    const result: Record<string, number[]> = {};
    
    for (const [key, value] of pairs) {
        if (result[key]) {
            result[key].push(value);
        } else {
            result[key] = [value];
        }
    }
    
    return result;
}