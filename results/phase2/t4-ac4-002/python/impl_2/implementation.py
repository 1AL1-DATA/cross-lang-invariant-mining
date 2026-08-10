import re

def evaluate(expr: str) -> int:
    """Evaluate a simple arithmetic expression with +, -, *, / and integer
    precedence (multiply before add). Support parentheses. No unary minus.
    Returns the integer result."""
    # Remove whitespace and tokenise numbers and operators
    expr = expr.replace(' ', '')
    tokens = re.findall(r'\d+|[+\-*/()]', expr)
    idx = 0

    def parse_expr():
        nonlocal idx
        left = parse_term()
        while idx < len(tokens) and tokens[idx] in '+-':
            op = tokens[idx]
            idx += 1
            right = parse_term()
            if op == '+':
                left += right
            else:
                left -= right
        return left

    def parse_term():
        nonlocal idx
        left = parse_factor()
        while idx < len(tokens) and tokens[idx] in '*/':
            op = tokens[idx]
            idx += 1
            right = parse_factor()
            if op == '*':
                left *= right
            else:
                left //= right   # integer division
        return left

    def parse_factor():
        nonlocal idx
        token = tokens[idx]
        if token == '(':
            idx += 1
            value = parse_expr()
            if tokens[idx] != ')':
                raise ValueError('Missing closing parenthesis')
            idx += 1
            return value
        else:
            idx += 1
            return int(token)

    return parse_expr()