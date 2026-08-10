function flatten(lst: any[]): any[] {
    const result: any[] = [];
    
    for (const item of lst) {
        if (Array.isArray(item)) {
            result.push(...flatten(item));
        } else {
            result.push(item);
        }
    }
    
    return result;
}