pub fn solution(data: Vec<i32>) -> Vec<i32> {
    data.into_iter().filter(|&x| x > 0).collect()
}
