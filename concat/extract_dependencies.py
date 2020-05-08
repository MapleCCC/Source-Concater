import re
from pathlib import Path
from typing import List, Optional, Set

from .constants import INCLUDE_NON_SYS_HEADER_PATTERN, IS_HEADER_FILE
from .process_c_source import dummify_string_literals, remove_comments


def seek_file(relative_path: Path, possible_dir: List[Path]) -> Optional[Path]:
    for path in possible_dir:
        candidate = path / relative_path
        if candidate.is_file():
            return candidate
    return None


# TODO: further revision is needed to add robustness to the search
# TODO: handle unlikey case that both C and C++ implementation exist
def get_implem_from_header(filepath: Path, source_dir: List[Path]) -> Optional[Path]:
    """
    Heuristic search
    Return None if no corresponding implementation file is found
    """
    # sanity check
    assert IS_HEADER_FILE(filepath)
    c_implem = seek_file(Path(filepath.stem + ".c"), source_dir)
    cpp_implem = seek_file(Path(filepath.stem + ".cpp"), source_dir)

    if c_implem and c_implem.is_file():
        return c_implem
    elif cpp_implem and cpp_implem.is_file():
        return cpp_implem
    else:
        return None


def extract_dependencies_of_file(filepath: Path, include_dir: List[Path]) -> Set[Path]:
    content = filepath.read_text(encoding="utf-8")
    content = remove_comments(content)
    # FIXME
    # content = dummyfy_string_literals(content)
    matches = re.findall(INCLUDE_NON_SYS_HEADER_PATTERN, content)
    deps = set()
    for match in matches:
        abspath = seek_file(match, include_dir)
        if not abspath:
            raise FileNotFoundError(f"Can't find depedency of {filepath}: {match}")
        deps.add(abspath)
    return deps


def get_dependencies_of_library(
    filepath: Path, include_dir: List[Path], source_dir: List[Path]
) -> Set[Path]:
    deps = extract_dependencies_of_file(filepath, include_dir)
    if IS_HEADER_FILE(filepath):
        implem = get_implem_from_header(filepath, source_dir)
        if implem:
            deps |= extract_dependencies_of_file(implem, include_dir) - {filepath}
    return deps
