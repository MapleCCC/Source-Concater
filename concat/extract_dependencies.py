import os
import re
from typing import List, Optional, Set

from .constants import INCLUDE_NON_STD_LIB_PATTERN, IS_HEADER_FILE
from .process_c_source import dummify_string_literals, remove_comments
from .utils import filebasename_without_ext, join_path


def seek_file(relative_path: str, possible_dir: List[str]) -> Optional[str]:
    for path in possible_dir:
        candidate = join_path(path, relative_path)
        if os.path.isfile(candidate):
            return candidate
    return None


# TODO: further revision is needed to add robustness to the search
# Handle possible cases that header files and implementation files
# are put in two separate directories.
# TODO: handle unlikey case that both C and C++ implementation exist
def get_implem_from_header(filepath: str, source_dir: List[str]) -> Optional[str]:
    """
    Heuristic search
    Return None if no corresponding implementation file is found
    """
    # sanity check
    assert IS_HEADER_FILE(filepath)
    c_implem = seek_file(filebasename_without_ext(filepath) + ".c", source_dir)
    cpp_implem = seek_file(filebasename_without_ext(filepath) + ".cpp", source_dir)

    if c_implem and os.path.isfile(c_implem):
        return c_implem
    elif cpp_implem and os.path.isfile(cpp_implem):
        return cpp_implem
    else:
        return None


def extract_dependencies_of_file(filepath: str, include_dir: List[str]) -> Set[str]:
    content = Path(filepath).read_text(encoding="utf-8")
    content = remove_comments(content)
    # FIXME
    # content = dummyfy_string_literals(content)
    matches = re.findall(INCLUDE_NON_STD_LIB_PATTERN, content)
    # WARNING: On Windows, os.sep is '\\' (ie, a backslash character).
    # But the header file path in C file's #include directive uses '/' most of time.
    # We should not use os.path.join to do the path join job if we want portability.
    deps = set()
    for match in matches:
        abspath = seek_file(match, include_dir)
        if not abspath:
            raise FileNotFoundError(f"Can't find depedency of {filepath}: {match}")
        deps.add(abspath)
    return deps


def get_dependencies_of_library(
    filepath: str, include_dir: List[str], source_dir: List[str]
) -> Set[str]:
    deps = extract_dependencies_of_file(filepath, include_dir)
    if IS_HEADER_FILE(filepath):
        implem = get_implem_from_header(filepath, source_dir)
        if implem:
            deps |= extract_dependencies_of_file(implem, include_dir) - {filepath}
    return deps
