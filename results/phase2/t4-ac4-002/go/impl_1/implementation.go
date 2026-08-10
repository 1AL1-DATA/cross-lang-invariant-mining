package evaluator

type tokenType int

const (
	tokNumber tokenType = iota
	tokPlus
	tokMinus
	tokStar
	tokSlash
	tokLparen
	tokRparen
	tokEOF
)

type token struct {
	typ tokenType
	val int
}

type parser struct {
	input string
	pos   int
	cur   token
}

func (p *parser) skipWhitespace() {
	for p.pos < len(p.input) && p.input[p.pos] <= ' ' {
		p.pos++
	}
}

func (p *parser) next() {
	p.skipWhitespace()
	if p.pos >= len(p.input) {
		p.cur = token{typ: tokEOF}
		return
	}
	c := p.input[p.pos]
	switch c {
	case '+':
		p.cur = token{typ: tokPlus}
		p.pos++
	case '-':
		p.cur = token{typ: tokMinus}
		p.pos++
	case '*':
		p.cur = token{typ: tokStar}
		p.pos++
	case '/':
		p.cur = token{typ: tokSlash}
		p.pos++
	case '(':
		p.cur = token{typ: tokLparen}
		p.pos++
	case ')':
		p.cur = token{typ: tokRparen}
		p.pos++
	default:
		if c >= '0' && c <= '9' {
			val := 0
			for p.pos < len(p.input) && p.input[p.pos] >= '0' && p.input[p.pos] <= '9' {
				val = val*10 + int(p.input[p.pos]-'0')
				p.pos++
			}
			p.cur = token{typ: tokNumber, val: val}
		} else {
			panic("invalid character")
		}
	}
}

func (p *parser) parseExpression() int {
	left := p.parseTerm()
	for p.cur.typ == tokPlus || p.cur.typ == tokMinus {
		op := p.cur.typ
		p.next()
		right := p.parseTerm()
		if op == tokPlus {
			left = left + right
		} else {
			left = left - right
		}
	}
	return left
}

func (p *parser) parseTerm() int {
	left := p.parseFactor()
	for p.cur.typ == tokStar || p.cur.typ == tokSlash {
		op := p.cur.typ
		p.next()
		right := p.parseFactor()
		if op == tokStar {
			left = left * right
		} else {
			if right == 0 {
				panic("division by zero")
			}
			left = left / right
		}
	}
	return left
}

func (p *parser) parseFactor() int {
	if p.cur.typ == tokNumber {
		v := p.cur.val
		p.next()
		return v
	}
	if p.cur.typ == tokLparen {
		p.next()
		val := p.parseExpression()
		if p.cur.typ != tokRparen {
			panic("missing closing parenthesis")
		}
		p.next()
		return val
	}
	panic("unexpected token")
}

// Evaluate computes the integer result of a simple arithmetic expression.
// Supported operators: +, -, *, / with integer precedence and parentheses.
// No unary minus is supported.
func Evaluate(expr string) int {
	p := parser{input: expr}
	p.next()
	val := p.parseExpression()
	if p.cur.typ != tokEOF {
		panic("unexpected token after expression")
	}
	return val
}