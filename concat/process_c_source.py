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
        # raise NotImplementedError
        return content

    return remove_multi_line_comments(remove_single_line_comments(content))


def remove_include_non_std_lib_directive(content: str) -> str:
    new_lines = []
    past = None
    remove_blank_line_flag = False
    for line in content.splitlines():
        if re.match(INCLUDE_NON_STD_LIB_PATTERN, line):
            if past == "":
                remove_blank_line_flag = True
        elif remove_blank_line_flag:
            if line == "":
                pass
            else:
                remove_blank_line_flag = False
                new_lines.append(line)
        past = line
    return "\n".join(new_lines)


# TODO: sort includes, and separate includes according to categories. Refer to clang-format for example.
def move_include_std_lib_directive_to_top(content: str) -> str:
    lines = content.splitlines()
    includes = set()
    body = []
    past = None
    remove_blank_line_flag = False
    for line in lines:
        if re.match(INCLUDE_STD_LIB_PATTERN, line):
            includes.add(line)
            if past == "":
                remove_blank_line_flag = True
        elif remove_blank_line_flag:
            if line == "":
                pass
            else:
                remove_blank_line_flag = False
                body.append(line)
        past = line
    return "\n".join(sorted(includes) + [""] + body)
