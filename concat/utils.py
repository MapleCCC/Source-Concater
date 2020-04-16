import os
from typing import Optional

__all__ = ["get_file_content", "join_path", "get_implem_from_header"]


def get_file_content(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_file_content(filepath: str, content: str):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


# Further revision is required to enhance portability and robustness.
# WARNING: On Windows, os.sep is '\\' (ie, a backslash character).
# But the header file path in C file's #include directive uses '/' most of time.
# We should not use os.path.join to do the path join job if we want portability.
def join_path(*paths) -> str:
    """Naive and simple path join utility."""
    return "/".join(filter(lambda path: path is not "", paths))


# TODO: further revision is needed to add robustness to the search
# Handle possible cases that header files and implementation files
# are put in two separate directories.
def get_implem_from_header(filepath: str) -> Optional[str]:
    """
    Heuristic search
    Return None if no corresponding implementation file is found
    """
    # sanity check
    assert filepath.endswith(".h")
    c_implem = filepath[: -len(".h")] + ".c"
    cpp_implem = filepath[: -len(".h")] + ".cpp"
    # TODO: unlikey case that both C and C++ implementation exist
    if os.path.isfile(c_implem):
        return c_implem
    elif os.path.isfile(cpp_implem):
        return cpp_implem
    else:
        return None
    # return implem if os.path.isfile(implem) else None
