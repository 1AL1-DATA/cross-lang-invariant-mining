package factorial

import "errors"

var ErrOutOfRange = errors.New("n out of range: must be 0 <= n <= 20")

func Factorial(n int) (int, error) {
	if n < 0 || n > 20 {
		return 0, ErrOutOfRange
	}
	result := int64(1)
	for i := 2; i <= n; i++ {
		result *= int64(i)
	}
	return int(result), nil
}