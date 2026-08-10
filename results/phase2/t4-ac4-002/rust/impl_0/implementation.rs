use std::str::Chars;

pub fn evaluate(expr: &str) -> i32 {
    let mut parser = Parser::new(expr.chars().peekable());
    parser.parse()
}

struct Parser<'a> {
    chars: Chars<'a>,
    current: Option<char>,
}

impl<'a> Parser<'a> {
    fn new(chars: Chars<'a>) -> Self {
        let mut parser = Parser {
            chars,
            current: None,
        };
        parser.advance();
        parser
    }

    fn advance(&mut self) {
        self.current = self.chars.next();
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

    fn parse(&mut self) -> i32 {
        self.skip_whitespace();
        let result = self.expr();
        result
    }

    fn expr(&mut self) -> i32 {
        let mut result = self.term();
        loop {
            self.skip_whitespace();
            match self.current {
                Some('+') => {
                    self.advance();
                    result += self.term();
                }
                Some('-') => {
                    self.advance();
                    result -= self.term();
                }
                _ => break,
            }
        }
        result
    }

    fn term(&mut self) -> i32 {
        let mut result = self.factor();
        loop {
            self.skip_whitespace();
            match self.current {
                Some('*') => {
                    self.advance();
                    result *= self.factor();
                }
                Some('/') => {
                    self.advance();
                    result /= self.factor();
                }
                _ => break,
            }
        }
        result
    }

    fn factor(&mut self) -> i32 {
        self.skip_whitespace();
        match self.current {
            Some('(') => {
                self.advance();
                let result = self.expr();
                self.skip_whitespace();
                if self.current == Some(')') {
                    self.advance();
                }
                result
            }
            Some(c) if c.is_ascii_digit() => {
                let mut num_str = String::new();
                while let Some(d) = self.current {
                    if d.is_ascii_digit() {
                        num_str.push(d);
                        self.advance();
                    } else {
                        break;
                    }
                }
                num_str.parse().unwrap_or(0)
            }
            _ => 0,
        }
    }
}