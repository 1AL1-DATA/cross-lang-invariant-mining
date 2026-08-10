def evaluate(expr):
    expr = expr.replace(" ", "")
    pos = 0
    
    def parse_expr():
        nonlocal pos
        result = parse_term()
        while pos < len(expr):
            op = expr[pos]
            if op == '+' or op == '-':
                pos += 1
                term = parse_term()
                if op == '+':
                    result += term
                else:
                    result -= term
            else:
                break
        return result
    
    def parse_term():
        nonlocal pos
        result = parse_factor()
        while pos < len(expr):
            op = expr[pos]
            if op == '*' or op == '/':
                pos += 1
                factor = parse_factor()
                if op == '*':
                    result *= factor
                else:
                    result //= factor
            else:
                break
        return result
    
    def parse_factor():
        nonlocal pos
        if expr[pos] == '(':
            pos += 1
            result = parse_expr()
            pos += 1
            return result
        else:
            start = pos
            while pos < len(expr) and expr[pos].isdigit():
                pos += 1
            return int(expr[start:pos])
    
    return parse_expr()