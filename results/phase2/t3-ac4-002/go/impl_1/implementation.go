package main

import "sort"

func TopKElements(lst []int, k int) []int {
    if k <= 0 || k > len(lst) {
        return nil
    }
    
    sorted := make([]int, len(lst))
    copy(sorted, lst)
    
    sort.Sort(sort.Reverse(sort.IntSlice(sorted)))
    
    return sorted[:k]
}