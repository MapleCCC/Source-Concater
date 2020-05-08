import re
from pathlib import Path

__all__ = ["INCLUDE_NON_STD_LIB_PATTERN", "INCLUDE_STD_LIB_PATTERN", "IS_HEADER_FILE"]

# TODO: relax the regex
# TODO: Take care of the unlikely case when standard lib is surrounded by "" instead of <> in the #include directive.
# TODO: take care of any corner/edge cases that we could think of.
# TODO: it's possible to include .cpp files
# TODO: it's possible to include .hpp files
# TODO: it's possible to include .tpp files
INCLUDE_NON_STD_LIB_PATTERN = re.compile(r"#include\s+\"(.*\.(?:h|hpp|tpp))\"")
INCLUDE_STD_LIB_PATTERN = re.compile(r"#include\s+<(.*)>")

# TODO: rename "standard lbrary" to "system header"

# TODO: Enhance robustness. Handle more cases.
# currently only a sanity check.
def IS_HEADER_FILE(file: Path) -> bool:
    return file.suffix in (".h", ".hpp", ".tpp")
