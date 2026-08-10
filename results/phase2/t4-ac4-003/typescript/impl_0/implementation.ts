function composeNFunctions(funcs: Array<(x: number) => number>, x: number): number {
    let result = x;
    for (const func of funcs) {
        result = func(result);
    }
    return result;
}