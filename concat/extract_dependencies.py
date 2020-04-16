import os
import re
from typing import Set

from .process_c_source import remove_comments
from .utils import get_file_content, get_implem_from_header, join_path

# TODO: relax the regex
# TODO: Take care of the unlikely case when standard lib is surrounded by "" instead of <> in the #include directive.
# TODO: take care of any corner/edge cases that we could think of.
# TODO: it's possible to include .cpp files
# TODO: it's possible to include .hpp files
# TODO: it's possible to include .tpp files
INCLUDE_NON_STD_LIB_PATTERN = r"#include\s+\"(.*\.h)\""
INCLUDE_STD_LIB_PATTERN = r"#include\s+<(.*)>"


def extract_dependencies_of_file(filepath: str) -> Set[str]:
    content = get_file_content(filepath)
    # matches = (
    #     re.match(INCLUDE_NON_STD_LIB_PATTERN, line) for line in content.splitlines()
    # )
    # return set(
    #     # WARNING: On Windows, os.sep is '\\' (ie, a backslash character).
    #     # But the header file path in C file's #include directive uses '/' most of time.
    #     # We should not use os.path.join to do the path join job if we want portability.
    #     # os.path.join(os.path.dirname(filepath), match.group(1))
    #     join_path(os.path.dirname(filepath), match.group(1))
    #     for match in matches
    #     if match
    # )
    content = remove_comments(content)
    matches = re.findall(INCLUDE_NON_STD_LIB_PATTERN, content)
    return set(join_path(os.path.dirname(filepath), match) for match in matches)


def get_dependencies_of_library(filepath: str) -> Set[str]:
    deps = extract_dependencies_of_file(filepath)
    implem = get_implem_from_header(filepath)
    if implem:
        deps |= extract_dependencies_of_file(implem) - {filepath}
    return deps


# TODO: also remove trailing blank lines
def remove_include_non_std_lib_directive(content: str) -> str:
    return "\n".join(
        line
        for line in content.splitlines()
        if not re.match(INCLUDE_NON_STD_LIB_PATTERN, line)
    )


# TODO: also remove trailing blank lines
def move_include_std_lib_directive_to_top(content: str) -> str:
    lines = content.splitlines()
    includes = set()
    body = []
    for line in lines:
        if re.match(INCLUDE_STD_LIB_PATTERN, line):
            includes.add(line)
        else:
            body.append(line)
    return "\n".join(sorted(includes) + [""] + body)
