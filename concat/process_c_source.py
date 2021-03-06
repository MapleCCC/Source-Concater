import re
import shutil
import subprocess
from subprocess import CalledProcessError

from .config import DEFAULT_FORMATTER
from .constants import INCLUDE_NON_SYS_HEADER_PATTERN, INCLUDE_SYS_HEADER_PATTERN


def reformat_source(
    source: str, format_style: str, format_fallback_style: str, assume_filename: str
) -> str:
    if not shutil.which(DEFAULT_FORMATTER):
        raise RuntimeError("Couldn't find `clang-format` in PATH.")

    try:
        return subprocess.run(
            [
                DEFAULT_FORMATTER,
                "-style",
                format_style,
                "-fallback-style",
                format_fallback_style,
                # Specify assume-filename so clang-format can properly detect language
                "-assume-filename",
                assume_filename,
            ],
            input=source,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        ).stdout
    except CalledProcessError:
        raise RuntimeError("Error when formatting concated source code file")


# FIXME
def dummify_string_literals(content: str) -> str:
    DUMMY_CHARACTER = "0"
    # Use a negative lookbehind assertion to exclude escaped quotes
    matches = re.finditer(r"(?<!\\)\"", content)
    indices = list(map(lambda m: m.start(), matches))
    if len(indices) % 2 != 0:
        raise ValueError("Source file is syntax-wise invalid")
    start_quotes = indices[::2]
    end_quotes = indices[1::2]
    for start, end in zip(start_quotes, end_quotes):
        content = (
            content[: start + 1] + DUMMY_CHARACTER * (end - start - 1) + content[end:]
        )
    return content


def remove_comments(content: str) -> str:
    def remove_single_line_comments(content: str) -> str:
        lines = content.splitlines()
        out = []
        for line in lines:
            index = line.find("//")
            if index != -1:
                out.append(line[:index])
            else:
                out.append(line)
        return "\n".join(out)

    def remove_multi_line_comments(content: str) -> str:
        raise NotImplementedError

    # FIXME
    # return remove_multi_line_comments(remove_single_line_comments(content))
    return remove_single_line_comments(content)


def remove_include_non_sys_header_directive(content: str) -> str:
    new_lines = []
    past = ""
    remove_blank_line_flag = False
    for line in content.splitlines():
        if re.match(INCLUDE_NON_SYS_HEADER_PATTERN, line):
            if past == "":
                remove_blank_line_flag = True
        elif line == "":
            if remove_blank_line_flag:
                pass
            else:
                new_lines.append(line)
        else:
            remove_blank_line_flag = False
            new_lines.append(line)
        past = line
    # Add file-end newline to be POSIX-compatible
    return "\n".join(new_lines) + "\n"


# TODO: sort includes, and separate includes according to categories. Refer to clang-format for example.
def move_include_sys_header_directive_to_top(content: str) -> str:
    lines = content.splitlines()
    includes = set()
    body = []
    past = ""
    remove_blank_line_flag = False
    for line in lines:
        if re.match(INCLUDE_SYS_HEADER_PATTERN, line):
            includes.add(line)
            if past == "":
                remove_blank_line_flag = True
        elif line == "":
            if remove_blank_line_flag:
                pass
            else:
                body.append(line)
        else:
            remove_blank_line_flag = False
            body.append(line)
        past = line
    # Add file-end newline to be POSIX-compatible
    return "\n".join(sorted(includes) + [""] + body) + "\n"
