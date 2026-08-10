package main

import (
	"sort"
)

func topKElements(lst []int, k int) []int {
	arr := make([]int, len(lst))
	copy(arr, lst)

	sort.Slice(arr, func(i, j int) bool {
		return arr[i] > arr[j]
	})

	return arr[:k]
}