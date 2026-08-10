def parser_arithmetic_expression_evaluator(expr):
    """
    Evaluate a simple arithmetic expression with +, -, *, / and integer precedence
    (multiply/divide before add/subtract). Parentheses are supported; unary minus is not.
    Returns the integer result.
    """
    class Parser:
        def __init__(self, s):
            self.s = s.strip()
            self.pos = 0
            self.tokens = self._tokenize()

        def _tokenize(self):
            tokens = []
            i = 0
            n = len(self.s)
            while i < n:
                ch = self.s[i]
                if ch.isspace():
                    i += 1
                    continue
                if ch.isdigit():
                    j = i
                    while j < n and self.s[j].isdigit():
                        j += 1
                    tokens.append(('NUM', int(self.s[i:j])))
                    i = j
                elif ch in '+-*/()':
                    tokens.append(('OP', ch))
                    i += 1
                else:
                    raise ValueError(f"Invalid character: {ch}")
            return tokens

        def parse(self):
            result = self._parse_expr()
            if self.pos != len(self.tokens):
                raise ValueError("Unexpected tokens after parsing")
            return result

        def _parse_expr(self):
            left = self._parse_term()
            while (self.pos < len(self.tokens) and
                   self.tokens[self.pos][0] == 'OP' and
                   self.tokens[self.pos][1] in '+-'):
                op = self.tokens[self.pos][1]
                self.pos += 1
                right = self._parse_term()
                if op == '+':
                    left += right
                else:
                    left -= right
            return left

        def _parse_term(self):
            left = self._parse_factor()
            while (self.pos < len(self.tokens) and
                   self.tokens[self.pos][0] == 'OP' and
                   self.tokens[self.pos][1] in '*/'):
                op = self.tokens[self.pos][1]
                self.pos += 1
                right = self._parse_factor()
                if op == '*':
                    left *= right
                else:
                    # integer division (truncates toward zero)
                    left = int(left / right)
            return left

        def _parse_factor(self):
            if self.pos >= len(self.tokens):
                raise ValueError("Unexpected end of input")
            token = self.tokens[self.pos]
            if token[0] == 'NUM':
                self.pos += 1
                return token[1]
            elif token[0] == 'OP' and token[1] == '(':
                self.pos += 1
                val = self._parse_expr()
                if (self.pos < len(self.tokens) and
                    self.tokens[self.pos][0] == 'OP' and
                    self.tokens[self.pos][1] == ')'):
                    self.pos += 1
                    return val
                else:
                    raise ValueError("Missing closing parenthesis")
            else:
                raise ValueError(f"Unexpected token: {token}")

    parser = Parser(expr)
    return parser.parse()