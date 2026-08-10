package main

func CountCharacterFrequency(s string) map[string]int {
	counts := make(map[string]int)
	for _, r := range s {
		counts[string(r)]++
	}
	return counts
}