from typing import Callable, TypeVar

T = TypeVar("T")


def aggregate_by_length(
    arr: list[T], max_size: int, length_fn: Callable[[T], int]
) -> list[list[T]]:
    if len(arr) <= 1:
        return arr
    res: list[list[T]] = []
    cur: list[T] = []
    size = 0
    for x in arr:
        el = length_fn(x)
        if not cur or (size + el) <= max_size:
            cur.append(x)
            size += el
        else:
            res.append(cur)
            cur = [x]
            size = el
    if cur:
        res.append(cur)
    return res
