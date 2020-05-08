import os

__all__ = [
    "join_path",
    "filebasename_without_ext",
]


# Further revision is required to enhance portability and robustness.
# WARNING: On Windows, os.sep is '\\' (ie, a backslash character).
# But the header file path in C file's #include directive uses '/' most of time.
# We should not use os.path.join to do the path join job if we want portability.
def join_path(*paths: str) -> str:
    """Naive and simple path join utility."""
    return "/".join(paths)


def filebasename_without_ext(filepath: str) -> str:
    return os.path.splitext(os.path.basename(filepath))[0]
