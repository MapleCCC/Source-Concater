import re
from pathlib import Path

__all__ = ["INCLUDE_NON_SYS_HEADER_PATTERN", "INCLUDE_SYS_HEADER_PATTERN", "IS_HEADER_FILE"]

# TODO: Take care of the unlikely case when system header is surrounded by "" instead of <> in the #include directive.
# TODO: take care of any corner/edge cases that we could think of.
INCLUDE_NON_SYS_HEADER_PATTERN = re.compile(r"#include\s+\"(.*)\"")
INCLUDE_SYS_HEADER_PATTERN = re.compile(r"#include\s+<(.*)>")

# TODO: Enhance robustness. Handle more cases.
# currently only a sanity check.
def IS_HEADER_FILE(file: Path) -> bool:
    return file.suffix in (".h", ".hpp", ".tpp")
