package flatten

func Flatten(lst []interface{}) []interface{} {
	result := make([]interface{}, 0)

	var flatten func([]interface{})
	flatten = func(lst []interface{}) {
		for _, item := range lst {
			if nested, ok := item.([]interface{}); ok {
				flatten(nested)
			} else {
				result = append(result, item)
			}
		}
	}

	flatten(lst)
	return result
}