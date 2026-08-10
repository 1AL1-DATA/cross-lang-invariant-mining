def longest_common_subsequence(s1: str, s2: str) -> int:
    """
    Return the length of the longest common subsequence (LCS) of two strings.

    Parameters
    ----------
    s1 : str
        First string.
    s2 : str
        Second string.

    Returns
    -------
    int
        Length of the LCS.
    """
    if not s1 or not s2:
        return 0

    # Use the shorter string for the DP columns to minimize memory usage.
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    n, m = len(s1), len(s2)

    # dp_prev[j] will store the LCS length for the previous row.
    dp_prev = [0] * (m + 1)

    for i in range(1, n + 1):
        dp_curr = [0] * (m + 1)
        char_s1 = s1[i - 1]
        for j in range(1, m + 1):
            if char_s1 == s2[j - 1]:
                dp_curr[j] = dp_prev[j - 1] + 1
            else:
                # max of the cell above (dp_prev[j]) and the cell to the left (dp_curr[j-1])
                dp_curr[j] = dp_prev[j] if dp_prev[j] >= dp_curr[j - 1] else dp_curr[j - 1]
        dp_prev = dp_curr

    return dp_prev[m]