function evaluate(expr: string): number {
    let pos = 0;
    
    function skipWhitespace(): void {
        while (pos < expr.length && expr[pos] === ' ') {
            pos++;
        }
    }
    
    function parseNumber(): number {
        skipWhitespace();
        let num = 0;
        while (pos < expr.length && /\d/.test(expr[pos])) {
            num = num * 10 + parseInt(expr[pos]);
            pos++;
        }
        return num;
    }
    
    function parseFactor(): number {
        skipWhitespace();
        if (expr[pos] === '(') {
            pos++;
            const result = parseExpression();
            pos++;
            return result;
        }
        return parseNumber();
    }
    
    function parseTerm(): number {
        skipWhitespace();
        let result = parseFactor();
        while (pos < expr.length && (expr[pos] === '*' || expr[pos] === '/')) {
            const op = expr[pos];
            pos++;
            const right = parseFactor();
            if (op === '*') {
                result *= right;
            } else {
                result = Math.trunc(result / right);
            }
        }
        return result;
    }
    
    function parseExpression(): number {
        skipWhitespace();
        let result = parseTerm();
        while (pos < expr.length && (expr[pos] === '+' || expr[pos] === '-')) {
            const op = expr[pos];
            pos++;
            const right = parseTerm();
            if (op === '+') {
                result += right;
            } else {
                result -= right;
            }
        }
        return result;
    }
    
    return parseExpression();
}