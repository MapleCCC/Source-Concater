import os

__all__ = [
    "get_file_content",
    "write_file_content",
    "join_path",
    "filebasename_without_ext",
]


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
def join_path(*paths: str) -> str:
    """Naive and simple path join utility."""
    return "/".join(paths)


def filebasename_without_ext(filepath: str) -> str:
    return os.path.splitext(os.path.basename(filepath))[0]
