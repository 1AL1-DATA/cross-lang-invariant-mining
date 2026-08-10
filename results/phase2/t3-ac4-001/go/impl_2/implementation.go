package wordcount

import "strings"

// MapStep converts each line into a map of word frequencies.
func MapStep(lines []string) []map[string]int {
	result := make([]map[string]int, len(lines))
	for i, line := range lines {
		words := strings.Fields(line)
		counts := make(map[string]int)
		for _, w := range words {
			lower := strings.ToLower(w)
			counts[lower]++
		}
		result[i] = counts
	}
	return result
}

// ReduceStep merges a slice of word count maps into a single map.
func ReduceStep(maps []map[string]int) map[string]int {
	combined := make(map[string]int)
	for _, m := range maps {
		for word, count := range m {
			combined[word] += count
		}
	}
	return combined
}

// WordCount returns the total word frequencies for the given lines.
func WordCount(lines []string) map[string]int {
	intermediate := MapStep(lines)
	return ReduceStep(intermediate)
}