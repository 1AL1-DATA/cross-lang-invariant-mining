func Solution(data []int) []int {
    result := []int{}
    for _, x := range data {
        if x > 0 { result = append(result, x) }
    }
    return result
}
