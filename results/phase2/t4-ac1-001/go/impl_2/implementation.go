package anagram

func IsAnagram(s1, s2 string) bool {
	if len(s1) != len(s2) {
		return false
	}

	counts := make(map[rune]int)

	for _, r := range s1 {
		counts[r]++
	}

	for _, r := range s2 {
		counts[r]--
		if counts[r] < 0 {
			return false
		}
	}

	return true
}