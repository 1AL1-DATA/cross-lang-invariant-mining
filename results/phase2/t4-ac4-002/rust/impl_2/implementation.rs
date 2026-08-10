pub fn evaluate(expr: &str) -> Result<i64, String> {
    let chars: Vec<char> = expr.chars().collect();
    let mut parser = Parser { chars, pos: 0 };
    parser.skip_whitespace();
    let result = parser.parse_expression()?;
    parser.skip_whitespace();
    if parser.pos != parser.chars.len() {
        return Err("Unexpected character".to_string());
    }
    Ok(result)
}

struct Parser {
    chars: Vec<char>,
    pos: usize,
}

impl Parser {
    fn skip_whitespace(&mut self) {
        while self.pos < self.chars.len() && self.chars[self.pos].is_whitespace() {
            self.pos += 1;
        }
    }

    fn peek(&self) -> Option<char> {
        self.chars.get(self.pos).copied()
    }

    fn consume(&mut self) -> Option<char> {
        if self.pos < self.chars.len() {
            let ch = self.chars[self.pos];
            self.pos += 1;
            Some(ch)
        } else {
            None
        }
    }

    fn parse_expression(&mut self) -> Result<i64, String> {
        let mut value = self.parse_term()?;
        loop {
            self.skip_whitespace();
            match self.peek() {
                Some('+') => {
                    self.consume();
                    let right = self.parse_term()?;
                    value = value.checked_add(right).ok_or_else(|| "Overflow".to_string())?;
                }
                Some('-') => {
                    self.consume();
                    let right = self.parse_term()?;
                    value = value.checked_sub(right).ok_or_else(|| "Overflow".to_string())?;
                }
                _ => break,
            }
        }
        Ok(value)
    }

    fn parse_term(&mut self) -> Result<i64, String> {
        let mut value = self.parse_factor()?;