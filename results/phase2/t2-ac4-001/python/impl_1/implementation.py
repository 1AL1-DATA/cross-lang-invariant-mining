def group_by_key(pairs: list[tuple[str, int]]) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    for key, value in pairs:
        if key not in result:
            result[key] = []
        result[key].append(value)
    return result