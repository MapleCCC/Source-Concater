from os import PathLike
from typing import Union

# This type hint is extracted from builtin open function's type annotation
# Except int type, we don't include.
# It's also justified by the definition of `path-like object` in Python
# glossary (refer to the `path-like object` entry in https://docs.python.org/3.8/glossary.html)
Filename = Union[str, bytes, PathLike]
