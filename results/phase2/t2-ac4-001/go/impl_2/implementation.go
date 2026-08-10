package groupby

type Pair struct {
	Key   string
	Value int
}

func GroupByKey(pairs []Pair) map[string][]int {
	result := make(map[string][]int)
	for _, p := range pairs {
		result[p.Key] = append(result[p.Key], p.Value)
	}
	return result
}