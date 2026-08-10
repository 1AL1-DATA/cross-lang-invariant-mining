package main

func mergeSort(lst []int) []int {
	if len(lst) <= 1 {
		result := make([]int, len(lst))
		copy(result, lst)
		return result
	}

	mid := len(lst) / 2
	left := mergeSort(lst[:mid])
	right := mergeSort(lst[mid:])

	return merge(left, right)
}

func merge(left, right []int) []int {
	result := make([]int, 0, len(left)+len(right))
	i, j := 0, 0

	for i < len(left) && j < len(right) {
		if left[i] <= right[j] {
			result = append(result, left[i])
			i++
		} else {
			result = append(result, right[j])
			j++
		}
	}

	result = append(result, left[i:]...)
	result = append(result, right[j:]...)

	return result
}