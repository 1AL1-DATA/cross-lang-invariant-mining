def binary_search(arr: list[int], target: int) -> int:
    """Return the index of target in a sorted list, or -1 if not found."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1