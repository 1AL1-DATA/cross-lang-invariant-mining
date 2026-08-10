export function topKElements(lst: number[], k: number): number[] {
  if (k <= 0 || k > lst.length) {
    throw new Error('k must satisfy 0 < k <= lst.length');
  }
  // Clone and sort descending, then take the first k elements
  return [...lst].sort((a, b) => b - a).slice(0, k);
}