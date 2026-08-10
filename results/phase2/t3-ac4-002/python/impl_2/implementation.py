import heapq

def top_k_elements(lst, k):
    return heapq.nlargest(k, lst)