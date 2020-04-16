import re


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
