package groupby

type Pair struct {
	Key   string
	Value int
}

func GroupByKey(pairs []Pair) map[string][]int {
	result := make(map[string][]int)
	for _, pair := range pairs {
		result[pair.Key] = append(result[pair.Key], pair.Value)
	}
	return result
}