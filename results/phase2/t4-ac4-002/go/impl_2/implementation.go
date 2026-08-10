package parser

import (
	"fmt"
	"strconv"
	"unicode"
)

var ErrInvalidSyntax = fmt.Errorf("invalid syntax")

func Evaluate(expr string) (int, error) {
	tokens := tokenize(expr)
	if len(tokens) == 0 {
		return 0, ErrInvalidSyntax
	}
	p := &parser{tokens: tokens, pos: 0}
	return p.parseExpression()
}

type parser struct {
	tokens []token
	pos    int
}

type tokenType int

const (
	tokenNumber tokenType = iota
	tokenPlus
	tokenMinus
	tokenMul
	tokenDiv
	tokenLParen
	tokenRParen
)

type token struct {
	typ tokenType
	val int
}

func tokenize(expr string) []token {
	var tokens []token
	i := 0
	for i < len(expr) {
		r := rune(expr[i])
		if unicode.IsSpace(r) {
			i++
			continue
		}
		switch r {
		case '+':
			tokens = append(tokens, token{typ: tokenPlus})
			i++
		case '-':
			tokens = append(tokens, token{typ: tokenMinus})
			i++
		case '*':
			tokens = append(tokens, token{typ: tokenMul})
			i++
		case '/':
			tokens = append(tokens, token{typ: tokenDiv})
			i++
		case '(':
			tokens = append(tokens, token{typ: tokenLParen})
			i++
		case ')':
			tokens = append(tokens, token{typ: tokenRParen})
			i++
		default:
			if unicode.IsDigit(r) {
				j := i
				for j < len(expr) && unicode.IsDigit(rune(expr[j])) {
					j++
				}
				val, _ := strconv.Atoi(expr[i:j])
				tokens = append(tokens, token{typ: tokenNumber, val: val})
				i = j
			} else {
				i++
			}
		}
	}
	return tokens
}

func (p *parser) parseExpression() (int, error) {
	result, err := p.parseTerm()
	if err != nil {
		return 0, err
	}
	for p.pos < len(p.tokens) && (p.tokens[p.pos].typ == tokenPlus || p.tokens[p.pos].typ == tokenMinus) {
		op := p.tokens[p.pos]
		p.pos++
		rhs, err := p.parseTerm()
		if err != nil {
			return 0, err
		}
		if op.typ == tokenPlus {
			result += rhs
		} else {
			result -= rhs
		}
	}
	return result, nil
}

func (p *parser) parseTerm() (int, error) {
	result, err := p.parseFactor()
	if err != nil {
		return 0, err
	}
	for p.pos < len(p.tokens) && (p.tokens[p.pos].typ == tokenMul || p.tokens[p.pos].typ == tokenDiv) {
		op := p.tokens[p.pos]
		p.pos++
		rhs, err := p.parseFactor()
		if err != nil {
			return 0, err
		}
		if op.typ == tokenMul {
			result *= rhs
		} else {
			if rhs == 0 {
				return 0, fmt.Errorf("division by zero")
			}
			result /= rhs
		}
	}
	return result, nil
}

func (p *parser) parseFactor() (int, error) {
	if p.pos >= len(p.tokens) {
		return 0, ErrInvalidSyntax
	}
	tok := p.tokens[p.pos]
	p.pos++
	switch tok.typ {
	case tokenNumber:
		return tok.val, nil
	case tokenLParen:
		val, err := p.parseExpression()
		if err != nil {
			return 0, err
		}
		if p.pos >= len(p.tokens) || p.tokens[p.pos].typ != tokenRParen {
			return 0, ErrInvalidSyntax
		}
		p.pos++
		return val, nil
	default:
		return 0, ErrInvalidSyntax
	}
}