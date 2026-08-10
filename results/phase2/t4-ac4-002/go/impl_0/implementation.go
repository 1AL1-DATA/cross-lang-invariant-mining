package parser

import (
	"strconv"
	"unicode"
)

func Evaluate(expr string) int {
	tokens := tokenize(expr)
	pos := 0
	return parseExpression(tokens, &pos)
}

func tokenize(expr string) []Token {
	var tokens []Token
	for i := 0; i < len(expr); {
		c := rune(expr[i])
		if unicode.IsSpace(c) {
			i++
		} else if unicode.IsDigit(c) {
			j := i
			for j < len(expr) && unicode.IsDigit(rune(expr[j])) {
				j++
			}
			num, _ := strconv.Atoi(expr[i:j])
			tokens = append(tokens, Token{Type: NUMBER, Value: num})
			i = j
		} else {
			switch c {
			case '+':
				tokens = append(tokens, Token{Type: PLUS})
			case '-':
				tokens = append(tokens, Token{Type: MINUS})
			case '*':
				tokens = append(tokens, Token{Type: MULTIPLY})
			case '/':
				tokens = append(tokens, Token{Type: DIVIDE})
			case '(':
				tokens = append(tokens, Token{Type: LPAREN})
			case ')':
				tokens = append(tokens, Token{Type: RPAREN})
			}
			i++
		}
	}
	return tokens
}

type TokenType int

const (
	NUMBER TokenType = iota
	PLUS
	MINUS
	MULTIPLY
	DIVIDE
	LPAREN
	RPAREN
)

type Token struct {
	Type  TokenType
	Value int
}

func parseExpression(tokens []Token, pos *int) int {
	result := parseTerm(tokens, pos)
	for *pos < len(tokens) && (tokens[*pos].Type == PLUS || tokens[*pos].Type == MINUS) {
		op := tokens[*pos].Type
		*pos++
		right := parseTerm(tokens, pos)
		if op == PLUS {
			result += right
		} else {
			result -= right
		}
	}
	return result
}

func parseTerm(tokens []Token, pos *int) int {
	result := parseFactor(tokens, pos)
	for *pos < len(tokens) && (tokens[*pos].Type == MULTIPLY || tokens[*pos].Type == DIVIDE) {
		op := tokens[*pos].Type
		*pos++
		right := parseFactor(tokens, pos)
		if op == MULTIPLY {
			result *= right
		} else {
			result /= right
		}
	}
	return result
}

func parseFactor(tokens []Token, pos *int) int {
	if *pos >= len(tokens) {
		return 0
	}
	token := tokens[*pos]
	if token.Type == LPAREN {
		*pos++
		result := parseExpression(tokens, pos)
		if *pos < len(tokens) && tokens[*pos].Type == RPAREN {
			*pos++
		}
		return result
	}
	if token.Type == NUMBER {
		*pos++
		return token.Value
	}
	return 0
}