from itertools import filterfalse
from typing import Callable, Iterable, Optional

__all__ = ["filtertrue"]


def filtertrue(iterable: Iterable, predicate: Optional[Callable] = None) -> Iterable:
    if predicate is None:
        predicate = bool
    return filterfalse(lambda x: not predicate(x), iterable)
