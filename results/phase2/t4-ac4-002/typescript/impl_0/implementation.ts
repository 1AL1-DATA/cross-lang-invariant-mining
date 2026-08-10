function evaluate(expr: string): number {
  let pos = 0;

  function peek(): string {
    return expr[pos];
  }

  function consume(): string {
    return expr[pos++];
  }

  function parseNumber(): number {
    let numStr = '';
    while (pos < expr.length && /\d/.test(peek())) {
      numStr += consume();
    }
    return parseInt(numStr, 10);
  }

  function parseFactor(): number {
    if (peek() === '(') {
      consume();
      const result = parseExpression();
      consume();
      return result;
    }
    return parseNumber();
  }

  function parseTerm(): number {
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
  }

  function parseExpression(): number {
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
  }

  return parseExpression();
}