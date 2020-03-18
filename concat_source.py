import argparse
import os
import re
from pprint import PrettyPrinter
from typing import *

from graph import *

# TODO: add cli option to remove multiple-inclusion guard
# TODO: add cli argument to specify output filepath

print = PrettyPrinter().pprint


def get_file_content(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


# Further revision is required to enhance portability and robustness.
def join_path(*paths) -> str:
    """Naive and simple path join utility."""
    return "/".join(filter(lambda path: path is not "", paths))


# TODO: relax the regex
# TODO: Take care of the unlikely case when standard lib is surrounded by "" instead of <> in the #include directive.
# TODO: take care of any corner/edge cases that we could think of.
INCLUDE_NON_STD_LIB_PATTERN = r"#include\s+\"(.*\.h)\""
INCLUDE_STD_LIB_PATTERN = r"#include\s+<(.*\.h)>"


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


# TODO: implement in more sane way. Use queue.
def generate_graph(entry: str) -> Graph:
    graph = Graph()
    waitlist = {entry}
    while waitlist:
        newlist = set()
        for elem in waitlist:
            if not graph.has_node(elem):
                if elem.endswith(".h"):
                    deps = get_dependencies_of_library(elem)
                else:
                    deps = extract_dependencies_of_file(elem)
                for dep in deps:
                    graph.add_edge((elem, dep))
                    if not graph.has_node(dep):
                        newlist.add(dep)
        waitlist = newlist
    return graph


# TODO: further revision is needed to add robustness to the search
def get_implem_from_header(filepath: str) -> Optional[str]:
    """
    Heuristic search
    Return None if no corresponding implementation file is found
    """
    # sanity check
    assert filepath.endswith(".h")
    implem = filepath[: -len(".h")] + ".c"
    return implem if os.path.isfile(implem) else None


def remove_include_non_std_lib_directive(content: str) -> str:
    return "\n".join(
        line
        for line in content.splitlines()
        if not re.match(INCLUDE_NON_STD_LIB_PATTERN, line)
    )


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


def main():
    parser = argparse.ArgumentParser("Concatenate C Source Files")
    parser.add_argument("entry")
    args = parser.parse_args()
    entry = args.entry

    graph = generate_graph(entry)
    back_edge = graph.detect_back_edge(entry)
    if back_edge:
        raise CircularDependencyError(
            f"Circular dependency detected!: '{back_edge[0]}'->'{back_edge[1]}'"
        )

    inv = graph.get_invert_graph()
    topo_sorted = list(inv.topological_sort())
    headers = topo_sorted[:-1]
    implems = list(filter(None, map(get_implem_from_header, headers)))
    concated = headers + [entry] + implems[::-1]  # type: ignore

    # insert blank line between file contents
    output = "\n".join(map(get_file_content, concated))
    output = remove_include_non_std_lib_directive(output)
    output = move_include_std_lib_directive_to_top(output)

    # Consider use flag "x" (ie, exclusive creation)
    with open("concated.c", "w", encoding="utf-8") as f:
        f.write(output)


if __name__ == "__main__":
    main()
