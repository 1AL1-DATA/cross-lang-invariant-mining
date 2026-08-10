type UnaryFunction = (x: number) => number;

function composeNFunctions(funcs: UnaryFunction[], x: number): number {
    let result = x;
    for (const func of funcs) {
        result = func(result);
    }
    return result;
}

export default composeNFunctions;