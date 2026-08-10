package fibonacci

func Iterative(n int) int {
    if n <= 1 {
        return n
    }
    
    prev, curr := 0, 1
    for i := 2; i <= n; i++ {
        prev, curr = curr, prev+curr
    }
    return curr
}