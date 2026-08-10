use std::str::Chars;

struct Parser<'a> {
    chars: Chars<'a>,
    current: Option<char>,
}

impl<'a> Parser<'a> {
    fn new(expr: &'a str) -> Self {
        let mut chars = expr.chars();
        let current = chars.next();
        Parser { chars, current }
    }

    fn advance(&mut self) -> Option<char> {
        self.current = self.chars.next();
        self.current
    }

    fn skip_whitespace(&mut self) {
        while let Some(c) = self.current {
            if c.is_whitespace() {
                self.advance();
            } else {
                break;
            }
        }
    }

    fn parse_number(&mut self) -> i64 {
        let mut num = 0i64;
        while let Some(c) = self.current {
            if c.is_ascii_digit() {
                num = num * 10 + (c as i64 - '0' as i64);
                self.advance();
            } else {
                break;
            }
        }
        num
    }

    fn parse_factor(&mut self) -> i64 {
        self.skip_whitespace();
        
        if self.current == Some('(') {
            self.advance();
            let result = self.parse_expression();
            self.skip_whitespace();
            if self.current == Some(')') {
                self.advance();
            }
            result
        } else {
            self.parse_number()
        }
    }

    fn parse_term(&mut self) -> i64 {
        self.skip_whitespace();
        let mut result = self.parse_factor();
        
        loop {
            self.skip_whitespace();
            match self.current {
                Some('*') => {
                    self.advance();
                    result *= self.parse_factor();
                }
                Some('/') => {
                    self.advance();
                    result /= self.parse_factor();
                }
                _ => break,
            }
        }
        result
    }

    fn parse_expression(&mut self) -> i64 {
        self.skip_whitespace();
        let mut result = self.parse_term();
        
        loop {
            self.skip_whitespace();
            match self.current {
                Some('+') => {
                    self.advance();
                    result += self.parse_term();
                }
                Some('-') => {
                    self.advance();
                    result -= self.parse_term();
                }
                _ => break,
            }
        }
        result
    }

    fn parse(&mut self) -> i64 {
        self.parse_expression()
    }
}

pub fn evaluate(expr: &str) -> i64 {
    let mut parser = Parser::new(expr);
    parser.parse()
}