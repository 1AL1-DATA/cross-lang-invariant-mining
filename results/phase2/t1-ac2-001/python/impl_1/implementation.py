def binary_search(arr, target):
    """
    Given a sorted integer array and a target, return the index of the target, or -1 if not found.
    
    Args:
        arr (list[int]): sorted integer array, ascending
        target (int): value to search for
    
    Returns:
        int: index of target in arr, or -1
    """
    if not arr:
        return -1
    
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] > target:
            high = mid - 1
        else:
            low = mid + 1
    
    return -1