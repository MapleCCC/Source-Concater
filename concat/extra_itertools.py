from typing import Callable, Iterable, Optional

__all__ = ["filtertrue"]


def filtertrue(iterable: Iterable, predicate: Optional[Callable] = None) -> Iterable:
    return filter(predicate, iterable)  # type: ignore
