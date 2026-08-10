pub fn longest_common_subsequence(s1: &str, s2: &str) -> i32 {
    let chars1: Vec<char> = s1.chars().collect();
    let chars2: Vec<char> = s2.chars().collect();
    
    let m = chars1.len();
    let n = chars2.len();
    
    // Create a 2D DP array with (m+1) x (n+1) dimensions
    // dp[i][j] = length of LCS of chars1[0..i] and chars2[0..j]
    let mut dp = vec![vec![0; n + 1]; m + 1];
    
    // Fill the DP table
    for i in 1..=m {
        for j in 1..=n {
            if chars1[i - 1] == chars2[j - 1] {
                dp[i][j] = dp[i - 1][j - 1] + 1;
            } else {
                dp[i][j] = dp[i - 1][j].max(dp[i][j - 1]);
            }
        }
    }
    
    dp[m][n] as i32
}