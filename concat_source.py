import argparse
import re
import os
from typing import *
from pprint import PrettyPrinter
from graph import *

# print = PrettyPrinter().pprint

# Naive and simple path join utility.
# Further revision is required to enhance portability and robustness.
def join_path(*paths) -> str:
    return "/".join(filter(lambda path: path is not "", paths))


# TODO: relax the regex
# TODO: Take care of the unlikely case when standard lib is surrounded by "" instead of <> in the #include directive.
# TODO: take care of any corner/edge cases that we could think of.
INCLUDE_PATTERN = r"#include \"(.*\.h)\""


def extract_dependencies_of_file(filepath: str) -> Set[str]:
    content = get_file_content(filepath)
    matches = (re.fullmatch(INCLUDE_PATTERN, line) for line in content.splitlines())
    return set(
        # WARNING: On Windows, os.sep is '\\' (ie, a backslash character).
        # But the header file path in C file's #include directive uses '/' most of time.
        # We should not use os.path.join to do the path join job if we want portability.
        # os.path.join(os.path.dirname(filepath), match.group(1))
        join_path(os.path.dirname(filepath), match.group(1))
        for match in matches
        if match
    )


def get_dependencies_of_library(filepath: str) -> Set[str]:
    deps = extract_dependencies_of_file(filepath)
    implem = get_implem_from_header(filepath)
    if implem:
        deps |= extract_dependencies_of_file(implem) - {filepath}
    return deps


# TODO: implement in more sane way. Use queue.
# TODO: add detection of circular
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


def get_file_content(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


# TODO: further revision is needed to add robustness to the search
# Heuristic search
# Return None is no corresponding implementation file is found
def get_implem_from_header(filepath: str) -> Optional[str]:
    # sanity check
    assert filepath.endswith(".h")
    implem = filepath[: -len(".h")] + ".c"
    if os.path.isfile(implem):
        return implem
    return None


def remove_include_directive(file: str) -> str:
    return "\n".join(
        line for line in file.splitlines() if not re.fullmatch(INCLUDE_PATTERN, line)
    )


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
    implems = list(filter(None, map(get_implem_from_header, headers[::-1])))
    concated = headers + [entry] + implems  # type: ignore

    # insert blank line between headers
    output = "\n\n".join(map(remove_include_directive, map(get_file_content, concated)))

    with open("concated.c", "w", encoding="utf-8") as f:
        f.write(output)


if __name__ == "__main__":
    main()
