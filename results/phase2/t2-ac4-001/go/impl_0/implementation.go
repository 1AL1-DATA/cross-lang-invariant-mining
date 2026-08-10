package main

func GroupByKey(pairs []struct {
	Key   string
	Value int
}) map[string][]int {
	result := make(map[string][]int)
	for _, pair := range pairs {
		result[pair.Key] = append(result[pair.Key], pair.Value)
	}
	return result
}