export function flatten<T = any>(lst: (T | T[])[]): T[] {
  const result: T[] = [];
  for (const item of lst) {
    if (Array.isArray(item)) {
      result.push(...flatten(item));
    } else {
      result.push(item);
    }
  }
  return result;
}