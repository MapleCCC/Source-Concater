import re
from .constants import INCLUDE_NON_STD_LIB_PATTERN, INCLUDE_STD_LIB_PATTERN


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
        return content

    return remove_multi_line_comments(remove_single_line_comments(content))


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
