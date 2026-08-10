package main

func WordCount(lines []string) map[string]int {
	counts := make(map[string]int)

	for _, line := range lines {
		word := ""
		for _, ch := range line {
			if ch == ' ' || ch == '\t' || ch == '\n' || ch == '\r' {
				if word != "" {
					counts[toLower(word)]++
					word = ""
				}
			} else {
				word += string(ch)
			}
		}
		if word != "" {
			counts[toLower(word)]++
		}
	}

	return counts
}

func toLower(s string) string {
	result := make([]byte, len(s))
	for i, b := range []byte(s) {
		if b >= 'A' && b <= 'Z' {
			result[i] = b + 32
		} else {
			result[i] = b
		}
	}
	return string(result)
}