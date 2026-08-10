function evaluate(expr: string): number {
    let pos = 0;
    
    const peek = () => expr[pos];
    const consume = () => expr[pos++];
    const isDigit = (c: string) => c >= '0' && c <= '9';
    
    const parseNumber = (): number => {
        let num = 0;
        while (pos < expr.length && isDigit(peek())) {
            num = num * 10 + parseInt(consume());
        }
        return num;
    };
    
    const parseFactor = (): number => {
        if (peek() === '(') {
            consume();
            const result = parseExpression();
            consume();
            return result;
        }
        return parseNumber();
    };
    
    const parseTerm = (): number => {
        let result = parseFactor();
        while (pos < expr.length && (peek() === '*' || peek() === '/')) {
            const op = consume();
            const right = parseFactor();
            if (op === '*') {
                result *= right;
            } else {
                result = Math.trunc(result / right);
            }
        }
        return result;
    };
    
    const parseExpression = (): number => {
        let result = parseTerm();
        while (pos < expr.length && (peek() === '+' || peek() === '-')) {
            const op = consume();
            const right = parseTerm();
            if (op === '+') {
                result += right;
            } else {
                result -= right;
            }
        }
        return result;
    };
    
    return parseExpression();
}